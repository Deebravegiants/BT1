# [H] Out-of-bounds write in SetSuitesHashSigAlgo when processing an oversized signature algorithms list,...

## Summary
Severity: High
Advisory: JLSEC-2026-746
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-746
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Out-of-bounds write in SetSuitesHashSigAlgo when processing an oversized signature algorithms list, allowing a write past the bounds of the destination buffer.

## References
- https://github.com/advisories/GHSA-xpf5-wwvx-w945
- https://github.com/wolfSSL/wolfssl/pull/10204
- https://nvd.nist.gov/vuln/detail/CVE-2026-6325
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
