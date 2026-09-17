# [H] Concrete does not validate a CSRF token before processing requests to `/dashboard/extend/update/do_update/<pkgHandle>`

## Summary
Severity: High
Advisory: GHSA-jr5g-qv3g-rxxx
CVE: CVE-2026-8417
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-jr5g-qv3g-rxxx
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below does not validate a CSRF token before processing requests to /dashboard/extend/update/do_update/<pkgHandle>. The do_update() method in concrete/controllers/single_page/dashboard/extend/update.php checks only canInstallPackages() before executing upgradeCoreData() and upgrade() on the named package's controller. Because the endpoint is a state-changing GET route with no token enforcement, an attacker can force an authenticated administrator to trigger a package upgrade via a single cross-site navigation.In order to be vulnerable, the victim must be passing canInstallPackages() and and a target package must already be already installed. The Concrete CMS security team thanks @maru1009 for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8417
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
