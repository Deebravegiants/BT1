# [?] fix(core): avoid race condition when collecting qstrs

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-08-24
Source: https://github.com/trezor/trezor-firmware/commit/083bc87fb7e34b7c90bc6c053765f06499d3a274
Type: security-commit

## Details
fix(core): avoid race condition when collecting qstrs

[no changelog]

## Patch
### core/embed/rust/librust_qstr.h
```diff
@@ -15,7 +15,6 @@ static void _librust_qstrs(void) {
   MP_QSTR_7;
   MP_QSTR_8;
   MP_QSTR_9;
-  MP_QSTR_;
   MP_QSTR_ACK;
   MP_QSTR_ALERT;
   MP_QSTR_APP_HEADER_LEN;
```

### core/embed/rust/librust_qstr.h.mako
```diff
@@ -6,21 +6,30 @@
 
 static void _librust_qstrs(void) {
 <%
+import json
 import subprocess
 import sys
 from pathlib import Path
 from typing import Union, Set
 
 RUST_SRC = THIS_FILE.parent / "src"
 
-def find_unique_patterns_in_dir(directory: Union[str, Path], pattern: str) -> Set[str]:
-    command = f"grep -ro '{pattern}' {directory}"
-    result = subprocess.run(command, stdout=subprocess.PIPE, text=True, shell=True)
-    output_lines = result.stdout.strip().split("\n")
-    return set([line.split(":", 1)[1] for line in output_lines if line])
+def find_qstrs_in_dir() -> set[str]:
+    pattern = r"\bMP_QSTR_\w*"
+    # Avoid processing generated files here, to avoid the following race condition:
+    # * If translations are updated, `translated_string.rs` is updated via `translated_string.rs.mako`.
+    # * This template may be processed concurrently, and use an older version of `translated_string.rs`.
+    # (see https://github.com/trezor/trezor-firmware/issues/7338)
+    args = ["grep", "-ro", "--exclude-dir=generated", pattern, RUST_SRC]
+    output_lines = subprocess.check_output(args, text=True).strip().split("\n")
+    return {line.split(":", 1)[1] for line in output_lines if line}
 
-pattern = r"\bMP_QSTR_\w*"
-qstrings = find_unique_patterns_in_dir(RUST_SRC, pattern)
+def find_qstrs_from_translations() -> set[str]:
+    # Add qstrs for translation IDs (see `translated_string.rs.mako`)
+    en_data = json.loads((ROOT / "core" / "translations" / "en.json").read_text())
+    return {f"MP_QSTR_{name}" for name in en_data["translations"]}
+
+qstrings = find_qstrs_in_dir() | find_qstrs_from_translations()
 
 qstrings_universal = set()
 for prefix in ALTCOIN_PREFIXES:
```
