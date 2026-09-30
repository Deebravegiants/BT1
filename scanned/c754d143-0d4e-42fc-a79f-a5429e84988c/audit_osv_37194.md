# [M] SuiteCRM vulnerable to authenticated SSRF via PDF export

## Summary
Severity: Medium
Advisory: CVE-2026-29107
Aliases: GHSA-g7cv-4ghj-x98h
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-29107
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Prior to versions 7.15.1 and 8.9.3, it is possible to create PDF templates with `<img>` tags. When a PDF is exported using this template, the content (for example, `<img src=http://{burp_collaborator_url}>` is rendered server side, and thus a request is issued from the server, resulting in Server-Side Request Forgery. Versions 7.15.1 and 8.9.3 patch the issue.

## References
- https://docs.suitecrm.com/admin/releases/7.15.x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29107.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-g7cv-4ghj-x98h
- https://nvd.nist.gov/vuln/detail/CVE-2026-29107
