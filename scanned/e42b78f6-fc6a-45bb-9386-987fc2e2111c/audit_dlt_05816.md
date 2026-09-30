# [?] chore(ci): exception for RUSTSEC-2026-0222 (#16153)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-08-03
Source: https://github.com/near/nearcore/commit/64867b1ed96705f1b194db1b0e7f107946470750
Type: security-commit

## Details
chore(ci): exception for RUSTSEC-2026-0222 (#16153)

Our code is not affected by this, so we don't need to do anything other
than add an exception.

The exception can be removed when we update to the next Wasmtime LTS
version.

## Patch
### .cargo/audit.toml
```diff
@@ -35,4 +35,9 @@ ignore = [
     # S3/cloud-storage XML responses, not untrusted input. Remove once the upstream S3 crates upgrade.
     "RUSTSEC-2026-0194",
     "RUSTSEC-2026-0195",
+
+    # RUSTSEC-2026-0222: Wasmtime can only be affected when the embedder mixes
+    # objects from one Engine into a Store belonging to another Engine. Nearcore
+    # never mixes Engine-owned objects.
+    "RUSTSEC-2026-0222",
 ]
```
