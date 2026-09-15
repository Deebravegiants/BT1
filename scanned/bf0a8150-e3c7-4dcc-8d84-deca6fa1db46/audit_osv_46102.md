# [M] The side-channel protected T-Table implementation in wolfSSL up to version 5.6.5 protects against a...

## Summary
Severity: Medium
Advisory: JLSEC-2026-681
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-681
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
The side-channel protected T-Table implementation in wolfSSL up to version 5.6.5 protects against a side-channel attacker with cache-line resolution. In a controlled environment such as Intel SGX, an attacker can gain a per instruction sub-cache-line resolution allowing them to break the cache-line-level protection. For details on the attack refer to:  https://doi.org/10.46586/tches.v2024.i1.457-500

## References
- https://github.com/advisories/GHSA-w782-gjg9-cjx6
- https://github.com/wolfSSL/wolfssl/blob/master/ChangeLog.md#wolfssl-release-566-dec-19-2023
- https://nvd.nist.gov/vuln/detail/CVE-2024-1543
