# [M] Concrete CMS has an unauthorized file access issue

## Summary
Severity: Medium
Advisory: GHSA-fqg3-8w8r-8g94
CVE: CVE-2026-7879
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-fqg3-8w8r-8g94
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
In Concrete CMS 9.5.0 and below,  the submit_password() method in concrete/controllers/single_page/download_file.php allows unauthorized file access since downloading permission-restricted files bypasses the view_file permission check. Files without passwords can be downloaded and any user who knows a file's password can download a password protected file regardless of whether they have permission to access the file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7879
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
