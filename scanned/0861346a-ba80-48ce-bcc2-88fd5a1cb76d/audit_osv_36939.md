# [M] GetSimple CMS:  Cross-Site Request Forgery (CSRF) in File Upload Allows Arbitrary Uploads

## Summary
Severity: Medium
Advisory: CVE-2026-27146
Aliases: GHSA-26rv-8wpp-q84r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-27146
Type: osv

## Details
GetSimple CMS is a content management system. All versions of GetSimple CMS do not implement CSRF protection on the administrative file upload endpoint. As a result, an attacker can craft a malicious web page that silently triggers a file upload request from an authenticated victim’s browser. The request is accepted without requiring a CSRF token or origin validation. This allows an attacker to upload arbitrary files to the application without the victim’s knowledge or consent. In order to exploit this vulnerability, the victim must be authenticated to GetSimple CMS (e.g., admin user), and visit an attacker-controlled webpage. This issue does not have a fix at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27146.json
- https://github.com/GetSimpleCMS-CE/GetSimpleCMS-CE/security/advisories/GHSA-26rv-8wpp-q84r
- https://nvd.nist.gov/vuln/detail/CVE-2026-27146
