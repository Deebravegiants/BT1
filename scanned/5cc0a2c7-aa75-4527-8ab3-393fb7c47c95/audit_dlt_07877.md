# [?] Bump nim-websock: fix crash when sending >1mb (#3831)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-07-01
Source: https://github.com/status-im/nimbus-eth2/commit/4fbbbfd4624a5de674711361b2754601225a69e3
Type: security-commit

## Details
Bump nim-websock: fix crash when sending >1mb (#3831)

## Patch
### vendor/nim-websock
```diff
@@ -1 +1 @@
-Subproject commit 283a9bb1fccc91fc9ab840609f57788cd19d0d24
+Subproject commit 92d350fe88d4c3604f4a605bdef18de1902d1ab6
```
