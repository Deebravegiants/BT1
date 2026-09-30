# [?] chore: ignore `RUSTSEC-2024-0370` (#12126)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-09-23
Source: https://github.com/near/nearcore/commit/b079a53f750b1a4028f799d59772be73850b6439
Type: security-commit

## Details
chore: ignore `RUSTSEC-2024-0370` (#12126)

Fixes the CI.

## Patch
### .cargo/audit.toml
```diff
@@ -27,4 +27,8 @@ ignore = [
     # older versions of parking-lot are vulnerable, but used by wasmer0, which we need to keep alive for replayability reasons.
     # We should remove it, as well as this ignore, as soon as we get limited replayability.
     "RUSTSEC-2020-0070",
+
+    # proc-macro-error is unmaintained, but hard to replace right now.
+    # Follow https://github.com/Kyuuhachi/syn_derive/issues/4
+    "RUSTSEC-2024-0370",
 ]
```
