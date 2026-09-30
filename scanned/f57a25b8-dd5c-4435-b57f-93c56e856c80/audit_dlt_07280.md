# [?] chore: ignore RUSTSEC-2024-0384 (#12431)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-11-11
Source: https://github.com/near/nearcore/commit/a03f42c8d21a0ea553776b483d2b6ef540a7ba40
Type: security-commit

## Details
chore: ignore RUSTSEC-2024-0384 (#12431)

instant & derivative are breaking audit in CI:

https://github.com/near/nearcore/actions/runs/11779066830/job/32806748238

This is a poor fix. Please let me know if we should find a proper one.

## Patch
### .cargo/audit.toml
```diff
@@ -31,4 +31,12 @@ ignore = [
     # proc-macro-error is unmaintained, but hard to replace right now.
     # Follow https://github.com/Kyuuhachi/syn_derive/issues/4
     "RUSTSEC-2024-0370",
+
+    # The instant package is unmaintained, but hard to replace right now because
+    # parking_lot depends on it.
+    "RUSTSEC-2024-0384",
+
+    # The derivative package is unmainained, but hard to replace right now
+    # because ark-poly depends on it.
+    "RUSTSEC-2024-0388"
 ]
```
