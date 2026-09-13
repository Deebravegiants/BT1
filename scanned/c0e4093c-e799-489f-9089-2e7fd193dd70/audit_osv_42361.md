# [M] X.509 name constraint bypass via Subject CN treated as a DNS name

## Summary
Severity: Medium
Advisory: CVE-2026-6731
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-6731
Type: osv

## Details
X.509 name constraint bypass via the Subject Common Name when treated as a DNS-type name. A certificate whose Subject CN violates an issuing CA's DNS name constraints could be accepted.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6731.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6731
- https://github.com/wolfSSL/wolfssl/pull/10223
- https://github.com/wolfSSL/wolfssl
