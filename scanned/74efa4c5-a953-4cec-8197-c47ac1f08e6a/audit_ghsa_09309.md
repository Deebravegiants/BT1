# [H] Concrete CMS contains a CSRF vulnerability

## Summary
Severity: High
Advisory: GHSA-4c8m-6fwx-m7xq
CVE: CVE-2026-8421
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-4c8m-6fwx-m7xq
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below contains a CSRF vulnerability in the install_package() method of concrete/controllers/single_page/dashboard/extend/install.php.  An attacker who can cause an authenticated administrator to visit a crafted page,  and who has placed or caused a package to be present under DIR_PACKAGES/<handle>/, can force the installation of that package without any CSRF protection. Package installation executes the package controller's install() method as the web server user, enabling remote code execution.  In order to be vulnerable, the victim must be passing canInstallPackages. The Concrete CMS security team thanks @maru1009 for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8421
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
