# [H] wrong STARTTLS connection reuse

## Summary
Severity: High
Advisory: CVE-2026-8286
Aliases: CURL-CVE-2026-8286
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-8286
Type: osv

## Details
A vulnerability exists where a new transfer that uses STARTTLS to upgrade the
connection might reuse an existing live connection even though the TLS
configuration mismatches so it should not.

## References
- https://curl.se/docs/CVE-2026-8286.html
- https://curl.se/docs/CVE-2026-8286.json
- https://hackerone.com/reports/3718195
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8286.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8286
