# [?] go: Ignore CVE-2024-8421 until 2024-10-01

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-09-06
Source: https://github.com/oasisprotocol/oasis-core/commit/7073d0ace51b002a60d5c654760dd02c71cf8daa
Type: security-commit

## Details
go: Ignore CVE-2024-8421 until 2024-10-01

## Patch
### go/.nancy-ignore
```diff
@@ -1 +1,2 @@
 CVE-2024-34478 # can be ignored as we only use a few crypto libraries from btcd
+CVE-2024-8421 until=2024-10-01  # no mitigation is currently available (2024-09-06)
```
