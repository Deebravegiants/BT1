# [C] Use-after-free in PQC hybrid key-share handling

## Summary
Severity: Critical
Advisory: JLSEC-2026-757
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-757
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.8.4+0 <5.9.2+0

## Details
Use-after-free in PQC hybrid key-share handling. This is an incomplete-fix follow-up to CVE-2026-5460 (released in 5.9.1): a malicious TLS 1.3 server sending a truncated PQC hybrid KeyShare can still trigger the error cleanup path to operate on freed memory.

## References
- https://github.com/advisories/GHSA-w9rp-wwm2-fwmr
- https://github.com/wolfSSL/wolfssl/pull/10327
- https://nvd.nist.gov/vuln/detail/CVE-2026-7531
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
