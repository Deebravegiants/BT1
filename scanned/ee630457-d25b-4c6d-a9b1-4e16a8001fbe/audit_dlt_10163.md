# [?] go: Ignore CVE-2026-56859 until golang.org/x/net releases a fix

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2026-08-19
Source: https://github.com/oasisprotocol/oasis-core/commit/26ed1c5f90e60a2a9d970024cb4394558bbecff8
Type: security-commit

## Details
go: Ignore CVE-2026-56859 until golang.org/x/net releases a fix

## Patch
### go/.nancy-ignore
```diff
@@ -1,2 +1,3 @@
 CVE-2021-43668 # the vulnerability does not affect us as we don't use LevelDB
-CVE-2026-56860 # ignore until golang.org/x/net releases a fix
\ No newline at end of file
+CVE-2026-56860 # ignore until golang.org/x/net releases a fix
+CVE-2026-56859 # ignore until golang.org/x/net releases a fix
\ No newline at end of file
```
