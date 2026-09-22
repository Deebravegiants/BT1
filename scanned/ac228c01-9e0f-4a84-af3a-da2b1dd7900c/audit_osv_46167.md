# [M] A CRL critical extension bypass exists in `ParseCRL_Extensions` where critical extensions are not...

## Summary
Severity: Medium
Advisory: JLSEC-2026-751
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-751
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
A CRL critical extension bypass exists in `ParseCRL_Extensions` where critical extensions are not properly enforced, allowing a crafted CRL with an unhandled critical extension to be accepted. This only affects builds with CRL support enabled and where a crafted CRL had a trusted signature when parsed.

## References
- https://github.com/advisories/GHSA-qpch-gjf6-c9gf
- https://github.com/wolfSSL/wolfssl/pull/10239
- https://nvd.nist.gov/vuln/detail/CVE-2026-6450
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
