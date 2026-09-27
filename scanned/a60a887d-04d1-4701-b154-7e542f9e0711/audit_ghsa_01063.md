# [C] Arbitrary File Write in iobroker.admin

## Summary
Severity: Critical
Advisory: GHSA-54xj-q58h-9x57
CVE: CVE-2019-10765
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-54xj-q58h-9x57
Type: github-advisory

## Affected
- npm: `iobroker.admin` — affected >=0 <3.6.12

## Details
Versions of `iobroker.admin` prior to 3.6.12 are vulnerable to Path Traversal. The package fails to restrict access to folders outside of the intended folder in the `/log/` route, which may allow attackers to include arbitrary files in the system. An attacker would need to be authenticated to perform the attack but the package has authentication disabled by default.


## Recommendation

Upgrade to version 3.6.12 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10765
- https://github.com/ioBroker/ioBroker.admin/commit/16b2b325ab47896090bc7f54b77b0a97ed74f5cd
- https://snyk.io/vuln/SNYK-JS-IOBROKERADMIN-534634
- https://www.npmjs.com/advisories/1346
