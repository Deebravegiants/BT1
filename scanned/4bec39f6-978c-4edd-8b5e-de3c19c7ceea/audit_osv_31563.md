# [M] bearer token leak on cross-protocol redirect

## Summary
Severity: Medium
Advisory: CVE-2025-14524
Aliases: CURL-CVE-2025-14524
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2025-14524
Type: osv

## Details
When an OAuth2 bearer token is used for an HTTP(S) transfer, and that transfer
performs a cross-protocol redirect to a second URL that uses an IMAP, LDAP,
POP3 or SMTP scheme, curl might wrongly pass on the bearer token to the new
target host.

## References
- http://www.openwall.com/lists/oss-security/2026/01/07/4
- https://curl.se/docs/CVE-2025-14524.html
- https://curl.se/docs/CVE-2025-14524.json
- https://hackerone.com/reports/3459417
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14524.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14524
