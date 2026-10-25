"""Environment probes are not source, semantic, or browser acceptance evidence."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "doctor.py"


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "portable environment checker is not implemented")
        spec = importlib.util.spec_from_file_location("dth_doctor_test", SCRIPT)
        self.doctor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.doctor)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "工作 区"
        self.browser = self.root / "browser"
        self.browser.write_text("test executable placeholder", encoding="utf-8")
        self.browser.chmod(0o700)
        self.module = self.root / "playwright.js"
        self.module.write_text("test module placeholder", encoding="utf-8")

    def transport(self, command, **kwargs):
        self.assertFalse(kwargs.get("shell", False))
        if command[-1] == "--version":
            return subprocess.CompletedProcess(command, 0, "v24.1.0\n", "")
        if any(str(value).endswith("check_math.cjs") for value in command):
            return subprocess.CompletedProcess(command, 0, '{"checked":2}', "")
        if "-e" in command:
            return subprocess.CompletedProcess(command, 0, json.dumps({
                "modulePath": str(self.module), "browserPath": str(self.browser),
            }), "")
        self.fail("Unexpected process: " + str(command))

    def probe(self, transport=None, **kwargs):
        with patch.dict(os.environ, {}, clear=True), \
             patch.object(self.doctor.shutil, "which", return_value="/test/node"), \
             patch.object(self.doctor.subprocess, "run", side_effect=transport or self.transport):
            return self.doctor.run_doctor(self.workspace, **kwargs)

    def check(self, report, name):
        return next(item for item in report["checks"] if item["id"] == name)

    def test_ready_environment_never_claims_conversion_or_browser_verified(self):
        report = self.probe()
        self.assertTrue(report["buildReady"])
        self.assertFalse(report["fullConversionVerified"])
        self.assertEqual(self.check(report, "browserExecutable")["status"], "pass")
        for name in ("sourceReading", "ocr", "semanticReview", "fileStorage", "visualReview"):
            self.assertEqual(self.check(report, name)["status"], "unverified")
        self.assertEqual(list(self.workspace.iterdir()), [], "Probe files must be removed")

    def test_missing_node_fails_basic_readiness_without_starting_any_process(self):
        with patch.dict(os.environ, {}, clear=True), \
             patch.object(self.doctor.shutil, "which", return_value=None), \
             patch.object(self.doctor.subprocess, "run") as run:
            report = self.doctor.run_doctor(self.workspace, node="absent-node")
        self.assertFalse(report["buildReady"])
        self.assertEqual(self.check(report, "node")["status"], "fail")
        run.assert_not_called()

    def test_playwright_process_exit_is_not_a_successful_browser_probe(self):
        def transport(command, **kwargs):
            if "-e" in command:
                return subprocess.CompletedProcess(command, 1, "", "Playwright requires Node.js 20 or higher")
            return self.transport(command, **kwargs)
        report = self.probe(transport)
        self.assertTrue(report["buildReady"])
        self.assertEqual(self.check(report, "playwright")["status"], "unverified")
        self.assertEqual(self.check(report, "browserExecutable")["status"], "unverified")
        self.assertFalse(report["fullConversionVerified"])

    def test_missing_explicit_browser_stays_unverified(self):
        with patch.dict(os.environ, {"BROWSER_EXECUTABLE": str(self.root / "absent")}, clear=True), \
             patch.object(self.doctor.shutil, "which", return_value="/test/node"), \
             patch.object(self.doctor.subprocess, "run", side_effect=self.transport):
            report = self.doctor.run_doctor(self.workspace)
        self.assertTrue(report["buildReady"])
        self.assertEqual(self.check(report, "browserExecutable")["status"], "unverified")

    def test_failed_math_probe_prevents_build_readiness(self):
        def transport(command, **kwargs):
            if any(str(value).endswith("check_math.cjs") for value in command):
                return subprocess.CompletedProcess(command, 1, "", "math resource failed")
            return self.transport(command, **kwargs)
        report = self.probe(transport)
        self.assertFalse(report["buildReady"])
        self.assertEqual(self.check(report, "math")["status"], "fail")

    def test_missing_resource_is_not_silently_accepted(self):
        skill = self.root / "incomplete-skill"
        skill.mkdir()
        report = self.probe(skill=skill)
        self.assertFalse(report["buildReady"])
        self.assertEqual(self.check(report, "resources")["status"], "fail")
        self.assertIn("SKILL.md", self.check(report, "resources")["detail"])

    def test_write_denied_prevents_readiness(self):
        with patch.object(self.doctor.tempfile, "TemporaryDirectory", side_effect=PermissionError):
            report = self.probe()
        self.assertFalse(report["buildReady"])
        self.assertEqual(self.check(report, "workspace")["status"], "fail")

    def test_workspace_and_report_inside_installation_are_rejected_before_writes(self):
        for workspace, out in ((ROOT, None), (ROOT / "do-not-create", None),
                               (self.workspace, ROOT / "do-not-write.json")):
            with self.subTest(workspace=workspace, out=out):
                with patch.object(self.doctor.tempfile, "TemporaryDirectory") as temporary, \
                     patch.object(self.doctor.subprocess, "run") as process:
                    report = self.doctor.run_doctor(workspace, out=out)
                self.assertFalse(report["buildReady"])
                temporary.assert_not_called()
                process.assert_not_called()
        self.assertFalse((ROOT / "do-not-create").exists())
        self.assertFalse((ROOT / "do-not-write.json").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_into_installation_does_not_bypass_workspace_boundary(self):
        link = self.root / "linked-skill"
        try:
            link.symlink_to(ROOT, target_is_directory=True)
        except OSError:
            self.skipTest("symlinks not permitted in this environment")
        report = self.probe(out=link / "do-not-write.json")
        self.assertFalse(report["buildReady"])
        self.assertFalse((ROOT / "do-not-write.json").exists())

    def test_report_outside_workspace_is_rejected(self):
        out = self.root / "elsewhere.json"
        report = self.probe(out=out)
        self.assertFalse(report["buildReady"])
        self.assertFalse(out.exists())

    def test_timeout_is_reported_without_success(self):
        def timeout(command, **kwargs):
            raise subprocess.TimeoutExpired(command, 10)
        report = self.probe(timeout)
        self.assertFalse(report["buildReady"])
        self.assertEqual(self.check(report, "node")["status"], "fail")

    def test_cli_works_from_foreign_directory_and_writes_utf8_report(self):
        foreign = self.root / "foreign"
        foreign.mkdir()
        out = self.workspace / "checks" / "环境.json"
        result = subprocess.run([sys.executable, str(SCRIPT), "--workspace", str(self.workspace),
                                 "--node", str(self.root / "absent-node"), "--out", str(out)],
                                cwd=foreign, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), report)
        self.assertFalse(report["buildReady"])
        self.assertFalse(report["fullConversionVerified"])
        self.assertEqual(list(foreign.iterdir()), [])

    def test_cli_json_remains_utf8_when_terminal_default_is_ascii(self):
        environment = dict(os.environ, PYTHONIOENCODING="ascii")
        result = subprocess.run([sys.executable, str(SCRIPT), "--workspace", str(self.workspace),
                                 "--node", str(self.root / "absent-node")],
                                env=environment, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stderr.decode("utf-8", errors="replace"))
        self.assertEqual(result.stderr, b"", "Environment failure must return JSON, not an encoding traceback")
        report = json.loads(result.stdout.decode("utf-8"))
        self.assertFalse(report["buildReady"])
        self.assertEqual(report["workspace"], str(self.workspace.resolve()))


if __name__ == "__main__":
    unittest.main()
