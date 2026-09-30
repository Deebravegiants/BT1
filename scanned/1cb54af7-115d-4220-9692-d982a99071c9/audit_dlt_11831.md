# [?] fix: issue where `ape test --showinternal` would cause crash [APE-782] (#1371)

## Summary
Severity: Unknown
Chain: Tooling
Component: ApeWorX/ape
Published: 2023-04-03
Source: https://github.com/ApeWorX/ape/commit/4cf4e6babf9d0ee4997b958686e3919fbb54b13c
Type: security-commit

## Details
fix: issue where `ape test --showinternal` would cause crash [APE-782] (#1371)

## Patch
### src/ape/pytest/runners.py
```diff
@@ -47,17 +47,14 @@ def pytest_exception_interact(self, report, call):
         if self.config_wrapper.pytest_config.getoption("showinternal"):
             relevant_tb = list(tb_frames)
         else:
-            relevant_tb = PytestTraceback(
-                [
-                    f
-                    for f in tb_frames
-                    if Path(f.path).as_posix().startswith(base)
-                    or Path(f.path).name.startswith("test_")
-                ]
-            )
+            relevant_tb = [
+                f
+                for f in tb_frames
+                if Path(f.path).as_posix().startswith(base) or Path(f.path).name.startswith("test_")
+            ]
 
         if relevant_tb:
-            call.excinfo.traceback = relevant_tb
+            call.excinfo.traceback = PytestTraceback(relevant_tb)
             report.longrepr = call.excinfo.getrepr(
                 funcargs=True,
                 abspath=Path.cwd(),
```

### tests/integration/cli/conftest.py
```diff
@@ -11,7 +11,7 @@
 from ape.managers.config import CONFIG_FILE_NAME
 
 from .test_plugins import ListResult
-from .utils import NodeId, project_names, project_skipper, projects_directory
+from .utils import NodeId, __project_names__, __projects_directory__, project_skipper
 
 
 class IntegrationTestModule:
@@ -94,7 +94,7 @@ def load(self, name: str) -> Path:
                 # Already copied.
                 return self.project_map[name]
 
-            project_source_dir = projects_directory / name
+            project_source_dir = __projects_directory__ / name
             project_dest_dir = project_folder / project_source_dir.name
             copy_tree(str(project_source_dir), str(project_dest_dir))
             self.project_map[name] = project_dest_dir
@@ -103,7 +103,7 @@ def load(self, name: str) -> Path:
     return ProjectDirCache()
 
 
-@pytest.fixture(autouse=True, params=project_names)
+@pytest.fixture(autouse=True, params=__project_names__)
 def project(request, config, project_dir_map):
     project_dir = project_dir_map.load(request.param)
     with config.using_project(project_dir) as project:
```

### tests/integration/cli/test_test.py
```diff
@@ -142,6 +142,18 @@ def test_uncaught_txn_err(setup_pytester, project, pytester, eth_tester_provider
     assert expected in str(result.stdout)
 
 
+@skip_projects_except("with-contracts")
+def test_show_internal(setup_pytester, project, pytester, eth_tester_provider):
+    _ = eth_tester_provider  # Ensure using EthTester for this test.
+    setup_pytester(project.path.name)
+    result = pytester.runpytest("--showinternal")
+    expected = """
+    raise vm_err from err
+E   ape.exceptions.ContractLogicError: Transaction failed.
+    """.strip()
+    assert expected in str(result.stdout)
+
+
 @skip_projects_except("test", "with-contracts")
 def test_test_isolation_disabled(setup_pytester, project, pytester, eth_tester_provider):
     # check the disable isolation option actually disables built-in isolation
```

### tests/integration/cli/utils.py
```diff
@@ -3,8 +3,8 @@
 
 import pytest
 
-projects_directory = Path(__file__).parent / "projects"
-project_names = [p.stem for p in projects_directory.iterdir() if p.is_dir()]
+__projects_directory__ = Path(__file__).parent / "projects"
+__project_names__ = [p.stem for p in __projects_directory__.iterdir() if p.is_dir()]
 
 
 def assert_failure(result, expected_output):
@@ -39,7 +39,7 @@ class ProjectSkipper:
     """
 
     def __init__(self):
-        self.projects: Dict[str, Dict] = {n: {} for n in project_names}
+        self.projects: Dict[str, Dict] = {n: {} for n in __project_names__}
 
     def __iter__(self):
         return iter(self.projects)
```
