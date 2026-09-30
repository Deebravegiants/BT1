# [?] go: Ignore CVE-2026-56860 until golang.org/x/net releases a fix

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2026-08-17
Source: https://github.com/oasisprotocol/oasis-core/commit/0d670127a54a0c7fa0163888bfeb9f6b8249face
Type: security-commit

## Details
go: Ignore CVE-2026-56860 until golang.org/x/net releases a fix

## Patch
### go/.nancy-ignore
```diff
@@ -1 +1,2 @@
 CVE-2021-43668 # the vulnerability does not affect us as we don't use LevelDB
+CVE-2026-56860 # ignore until golang.org/x/net releases a fix
\ No newline at end of file
```
