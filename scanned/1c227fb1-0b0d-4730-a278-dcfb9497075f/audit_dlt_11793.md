# [?] Ignore RUSTSEC-2026-0118 and RUSTSEC-2026-0119 until libp2p and zkm-sdk are updated

## Summary
Severity: Unknown
Chain: Ethereum
Component: grandinetech/grandine
Published: 2026-05-18
Source: https://github.com/grandinetech/grandine/commit/6b434cad08bc275dffd526e0de4f068c6f2953f5
Type: security-commit

## Details
Ignore RUSTSEC-2026-0118 and RUSTSEC-2026-0119 until libp2p and zkm-sdk are updated

## Patch
### .cargo/audit.toml
```diff
@@ -12,5 +12,8 @@ ignore = [
     # TODO: remove this when this no longer the case
     'RUSTSEC-2026-0098',
     'RUSTSEC-2026-0099',
-    'RUSTSEC-2026-0104'
+    'RUSTSEC-2026-0104',
+    # TODO: revisit once libp2p and zkm-sdk are updated
+    'RUSTSEC-2026-0118',
+    'RUSTSEC-2026-0119'
 ]
```
