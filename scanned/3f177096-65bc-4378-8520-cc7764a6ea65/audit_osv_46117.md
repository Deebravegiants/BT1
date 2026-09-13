# [M] Certificates with wildcard DNS SANs (e.g

## Summary
Severity: Medium
Advisory: JLSEC-2026-696
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-696
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Certificates with wildcard DNS SANs (e.g. *.example.com) bypassed CA name-constraint checks. A certificate with a wildcard DNS SAN that should be rejected by the issuing CA's permitted/excluded DNS name constraints could be accepted.

## References
- https://github.com/advisories/GHSA-m8r2-qgr6-4gqm
- https://github.com/wolfSSL/wolfssl/pull/10549
- https://nvd.nist.gov/vuln/detail/CVE-2026-10592
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
