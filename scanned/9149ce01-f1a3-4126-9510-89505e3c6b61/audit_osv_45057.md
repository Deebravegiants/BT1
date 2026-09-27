# [C] PYSEC-2024-103

## Summary
Severity: Critical
Advisory: PYSEC-2024-103
Aliases: CVE-2024-22419, GHSA-2q8v-3gqq-4f8p
Ecosystem: PyPI
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-18
Source: https://osv.dev/vulnerability/PYSEC-2024-103
Type: osv

## Affected
- PyPI: `vyper` — affected >=0 <55e18f6d128b2da8986adbbcccf1cd59a4b9ad6f, >=0 <0.4.0b1

## Details
Vyper is a Pythonic Smart Contract Language for the Ethereum Virtual Machine. The `concat` built-in can write over the bounds of the memory buffer that was allocated for it and thus overwrite existing valid data. The root cause is that the `build_IR` for `concat` doesn't properly adhere to the API of copy functions (for `>=0.3.2` the `copy_bytes` function). A contract search was performed and no vulnerable contracts were found in production. The buffer overflow can result in the change of semantics of the contract. The overflow is length-dependent and thus it might go unnoticed during contract testing. However, certainly not all usages of concat will result in overwritten valid data as we require it to be in an internal function and close to the return statement where other memory allocations don't occur. This issue has been addressed in 0.4.0.

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-2q8v-3gqq-4f8p
- https://github.com/vyperlang/vyper/issues/3737
- https://github.com/vyperlang/vyper/commit/55e18f6d128b2da8986adbbcccf1cd59a4b9ad6f
