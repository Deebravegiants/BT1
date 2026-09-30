# [?] go: Add CVE-2025-11065 temporarily to .nancy-ignore

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2025-10-08
Source: https://github.com/oasisprotocol/oasis-core/commit/de3cc372d902ceec8f04c8e40b74676e580d345d
Type: security-commit

## Details
go: Add CVE-2025-11065 temporarily to .nancy-ignore

## Patch
### go/.nancy-ignore
```diff
@@ -1,3 +1,4 @@
 CVE-2024-34478 # can be ignored as we only use a few crypto libraries from btcd
 CVE-2025-4673 until=2025-07-14  # no mitigation is currently available (2025-06-14)
 CVE-2021-43668 # the vulnerability does not affect us as we don't use LevelDB
+CVE-2025-11065 until=2025-12-01 # the vulnerability does not affect us
```
