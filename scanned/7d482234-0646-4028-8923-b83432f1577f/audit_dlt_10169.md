# [?] go: Add CVE-2026-26014 temporarily to .nancy-ignore

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2026-02-12
Source: https://github.com/oasisprotocol/oasis-core/commit/c4f908fdd2d0768aaaec8df0738108984ff96ffa
Type: security-commit

## Details
go: Add CVE-2026-26014 temporarily to .nancy-ignore

## Patch
### go/.nancy-ignore
```diff
@@ -2,3 +2,4 @@ CVE-2024-34478 # can be ignored as we only use a few crypto libraries from btcd
 CVE-2025-4673 until=2025-07-14  # no mitigation is currently available (2025-06-14)
 CVE-2021-43668 # the vulnerability does not affect us as we don't use LevelDB
 CVE-2025-11065 until=2025-12-01 # the vulnerability does not affect us
+CVE-2026-26014 until=2026-03-01 # requires upstream mitigation
```
