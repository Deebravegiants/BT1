# [H] Concrete CMS has Stored XSS through its height parameter

## Summary
Severity: High
Advisory: GHSA-9v2g-37mp-qpxf
CVE: CVE-2026-8203
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-9v2g-37mp-qpxf
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below has Stored XSS on the height parameter. The controller does not validate or sanitize $height. Any user with editor privileges can inject malicious JavaScript that executes in the context of any visitor's browser, potentially leading to session hijacking, credential theft, or other malicious actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8203
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
