# [?] go: Add CVE-2021-43668 to .nancy-ignore as we don't use LevelDB

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2025-06-14
Source: https://github.com/oasisprotocol/oasis-core/commit/cd69d3ede4c86684066e793b3c5d00a691ad6deb
Type: security-commit

## Details
go: Add CVE-2021-43668 to .nancy-ignore as we don't use LevelDB

## Patch
### go/.nancy-ignore
```diff
@@ -1,2 +1,3 @@
 CVE-2024-34478 # can be ignored as we only use a few crypto libraries from btcd
 CVE-2025-4673 until=2025-07-14  # no mitigation is currently available (2025-06-14)
+CVE-2021-43668 # the vulnerability does not affect us as we don't use LevelDB
```
