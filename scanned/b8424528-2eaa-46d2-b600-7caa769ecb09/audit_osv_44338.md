# [C] Concrete CMS 9.5.0 and below is vulnerable to CSRF on download() in the package install controller

## Summary
Severity: Critical
Advisory: CVE-2026-8140
Aliases: GHSA-r42c-3rr2-jrfp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-8140
Type: osv

## Details
Concrete CMS 9.5.0 and below does not validate a CSRF token before processing requests to /dashboard/extend/install/download/<remoteId>. The download() method in concrete/controllers/single_page/dashboard/extend/install.php checks only the canInstallPackages() permission before fetching a remote marketplace package and writing it to the server's DIR_PACKAGES directory. Because the endpoint is a state-changing GET route with no token enforcement, an attacker who can cause an authenticated administrator to visit a crafted page can force an arbitrary marketplace package to be downloaded. In order to be vulnerable, the victim must be passing canInstallPackages() and the site must be connected to the Concrete marketplace. The Concrete CMS security team gave this vulnerability a CVSS v.4.0 score of 7.5 with vector CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N. Thanks  https://github.com/maru1009  for reporting.

## References
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8140.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8140
- https://github.com/concretecms/concretecms
