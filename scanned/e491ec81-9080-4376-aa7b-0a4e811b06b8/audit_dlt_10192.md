# [?] go: Add CVE-2022-39389 to ignore list as it is non-applicable

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2022-11-22
Source: https://github.com/oasisprotocol/oasis-core/commit/fc1a00bfd37ce7ac08a32a7eb2abec9d848b6ded
Type: security-commit

## Details
go: Add CVE-2022-39389 to ignore list as it is non-applicable

## Patch
### go/.nancy-ignore
```diff
@@ -1,2 +1,3 @@
 CVE-2022-30591 # quic-go resource exhaustion through 0.27.0, 0.27.1 imported, false positive?
 CVE-2022-44797 # remove once tendermint uses btcd above or 0.23.2
+CVE-2022-39389 # can be ignored as we only use a few crypto libraries from btcd
```
