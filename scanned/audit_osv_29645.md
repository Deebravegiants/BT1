# [M] `fold (xor (shl 1, x), -1) -> (rotl ~1, x)` misoptimization in zksolc

## Summary
Severity: Medium
Advisory: CVE-2024-45056
Aliases: GHSA-fpx7-8vc6-frjj
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-08-29
Source: https://osv.dev/vulnerability/CVE-2024-45056
Type: osv

## Details
zksolc is a Solidity compiler for ZKsync. All LLVM versions since 2015 fold `(xor (shl 1, x), -1)` to `(rotl ~1, x)` if run with optimizations enabled. Here `~1` is generated as an unsigned 64 bits number (`2^64-1`). This number is zero-extended to 256 bits on EraVM target while it should have been sign-extended. Thus instead of producing `roti 2^256 - 1, x` the compiler produces `rotl 2^64 - 1, x`. Analysis has shown that no contracts were affected by the date of publishing this advisory. This issue has been addressed in version 1.5.3. Users are advised to upgrade and redeploy all contracts. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45056.json
- https://github.com/matter-labs/era-compiler-solidity/security/advisories/GHSA-fpx7-8vc6-frjj
- https://nvd.nist.gov/vuln/detail/CVE-2024-45056
- https://github.com/llvm/llvm-project/commit/e48237df95b49a36b8ffceb78c8a58f4be1b4344
