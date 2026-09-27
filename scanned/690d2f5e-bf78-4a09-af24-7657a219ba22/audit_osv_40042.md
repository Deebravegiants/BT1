# [C] CVE-2026-49103

## Summary
Severity: Critical
Advisory: CVE-2026-49103
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-49103
Type: osv

## Details
Webmin before 2.640 does not safely construct a filename for saving of an attachment within the mailboxes component. This occurs in mailboxes/detachall.cgi.

## References
- https://github.com/webmin/webmin/compare/2.630...2.640
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49103.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-49103
- https://github.com/webmin/webmin/commit/cf432879a14568c4bb44cd2f9e5a9bd0e168edc1
