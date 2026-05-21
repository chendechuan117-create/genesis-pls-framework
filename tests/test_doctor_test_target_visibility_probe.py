import importlib.util
from pathlib import Path


def _load_module():
    probe_path = Path(__file__).resolve().parents[1] / 'runtime' / 'scratch' / 'doctor_test_target_visibility_probe.py'
    spec = importlib.util.spec_from_file_location('doctor_test_target_visibility_probe', probe_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_doctor_suite_contains_workspace_absolute_probe_references_that_depend_on_doctor_workspace_identity():
    module = _load_module()
    result = module.run_audit()

    assert result['doctor_script_exists'] is True
    assert result['tests_dir_exists'] is True
    assert result['scratch_dir_exists'] is True
    assert result['doctor_test_files'] > 0
    assert result['summary']['has_workspace_abs_probe_tests'] is True
    assert result['summary']['all_workspace_abs_probe_tests_are_doctor_prefixed'] is True


def test_workspace_absolute_probe_references_and_repo_relative_probe_references_currently_coexist():
    module = _load_module()
    result = module.run_audit()

    assert result['summary']['has_repo_relative_probe_tests'] is True
    assert len(result['workspace_abs_without_repo_relative']) >= 1
