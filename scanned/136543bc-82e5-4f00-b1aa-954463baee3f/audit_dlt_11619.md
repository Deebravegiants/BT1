# [?] Problem (fix #179): potential race condition in coverage report merging (#180)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/chain-main
Published: 2020-10-15
Source: https://github.com/crypto-org-chain/chain-main/commit/fac7171143f2ce693534defc4cc506615d7a9f3b
Type: security-commit

## Details
Problem (fix #179): potential race condition in coverage report merging (#180)

Solution:
- name the repot files with uuid and do the merge after test finished
- hopefully codecov can collect multiple files automatically

## Patch
### .github/workflows/nix.yml
```diff
@@ -56,7 +56,7 @@ jobs:
       uses: codecov/codecov-action@v1
       with:
         token: ${{ secrets.CODECOV_TOKEN }}
-        file: ./coverage.txt
+        file: ./coverage.*.txt
         flags: integration_tests
     - name: Publish docker image
       if: github.ref == 'refs/heads/master' || startsWith(github.ref, 'refs/tags/')
```

### .gitignore
```diff
@@ -13,7 +13,7 @@
 build
 
 # Testing
-coverage.txt
+/coverage.*.txt
 /data
 __pycache__
 
@@ -23,4 +23,4 @@ frontend/dist
 frontend/.cache
 
 # Pystarport
-bot.yaml
\ No newline at end of file
+bot.yaml
```

### integration_tests/utils.py
```diff
@@ -2,7 +2,7 @@
 import socket
 import sys
 import time
-from pathlib import Path
+import uuid
 
 import yaml
 from dateutil.parser import isoparse
@@ -65,8 +65,8 @@ def cluster_fixture(config_path, base_port, tmp_path_factory, quiet=False):
     ini = data / "tasks.ini"
     ini.write_text(
         re.sub(
-            r"^command = .*/chain-maind",
-            "command = chain-maind-inst -test.coverprofile=%(here)s/coverage.out",
+            r"^command = (.*/)?chain-maind",
+            "command = chain-maind-inst -test.coverprofile=%(here)s/coverage.txt",
             ini.read_text(),
             count=1,
             flags=re.M,
@@ -92,10 +92,4 @@ def cluster_fixture(config_path, base_port, tmp_path_factory, quiet=False):
     supervisord.wait()
 
     # collect the coverage results
-    txt = (data / "coverage.out").read_text()
-    merged = Path("coverage.txt")
-    if merged.exists():
-        assert txt.startswith("mode: set")
-        txt = txt[10:]
-    with merged.open("a") as f:
-        f.write(txt)
+    (data / "coverage.txt").rename(f"coverage.{uuid.uuid1()}.txt")
```
