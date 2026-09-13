# [M] Plone allows remote users to modify arbitrary portraits

## Summary
Severity: Medium
Advisory: GHSA-jcwh-rj6j-vm75
CVE: CVE-2006-1711
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-jcwh-rj6j-vm75
Type: github-advisory

## Affected
- PyPI: `plone` — affected >=0 <2.0.6
- PyPI: `plone` — affected >=2.1.0
- PyPI: `plone` — affected 2.5-beta1

## Details
Plone 2.0.5, 2.1.2, and 2.5-beta1 does not restrict access to the (1) changeMemberPortrait, (2) deletePersonalPortrait, and (3) testCurrentPassword methods, which allows remote attackers to modify portraits.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-1711
- https://exchange.xforce.ibmcloud.com/vulnerabilities/25781
- https://github.com/plone/Plone
- https://web.archive.org/web/20060412111111/https://dev.plone.org/plone/ticket/5432
- https://web.archive.org/web/20060422195724/http://www.securityfocus.com/bid/17484
- http://www.debian.org/security/2006/dsa-1032
