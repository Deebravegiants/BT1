# [H] Concrete CMS does not validate a CSRF token before processing requests to `/dashboard/extend/update/prepare_remote_upgrade/<remoteMPID>`

## Summary
Severity: High
Advisory: GHSA-5rj5-gfmr-hrc3
CVE: CVE-2026-8426
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-5rj5-gfmr-hrc3
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below does not validate a CSRF token before processing requests to /dashboard/extend/update/prepare_remote_upgrade/<remoteMPID>. An attacker who controls the remote package returned for a known marketplace item ID can overwrite the package PHP on disk and force its upgrade() method to execute in a single browser navigation. This results in remote code execution as the web server user.   In order to be vulnerable, the victim must be passing canInstallPackages, victim site must be connected to the Concrete marketplace; and the attacker controls the package returned for a marketplace item ID already installed on the victim site. The Concrete CMS security team thanks @maru1009 for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8426
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
