# [M] When `HAVE_ENCRYPT_THEN_MAC` is configured, the implementation could fall back to MAC-then-Encrypt...

## Summary
Severity: Medium
Advisory: JLSEC-2026-743
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-743
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.7.2+0 <5.9.2+0

## Details
When `HAVE_ENCRYPT_THEN_MAC` is configured, the implementation could fall back to MAC-then-Encrypt rather than enforcing Encrypt-then-MAC.

## References
- https://github.com/advisories/GHSA-576m-xh9m-c774
- https://github.com/wolfSSL/wolfssl/pull/10167
- https://nvd.nist.gov/vuln/detail/CVE-2026-6092
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
