# [M] connection reuse ignores TLS requirement

## Summary
Severity: Medium
Advisory: CVE-2026-4873
Aliases: CURL-CVE-2026-4873
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-4873
Type: osv

## Details
A vulnerability exists where a connection requiring TLS incorrectly reuses an
existing unencrypted connection from the same connection pool. If an initial
transfer is made in clear-text (via IMAP, SMTP, or POP3), a subsequent request
to that same host bypasses the TLS requirement and instead transmit data
unencrypted.

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/7
- https://curl.se/docs/CVE-2026-4873.html
- https://curl.se/docs/CVE-2026-4873.json
- https://hackerone.com/reports/3621851
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4873.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4873
