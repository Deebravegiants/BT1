# [M] Review Board Cross-site scripting (XSS) vulnerability in the reviews dropdown

## Summary
Severity: Medium
Advisory: GHSA-6g7x-4c7m-g63m
CVE: CVE-2013-2209
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6g7x-4c7m-g63m
Type: github-advisory

## Affected
- PyPI: `reviewboard` — affected >=1.6 <1.6.17
- PyPI: `reviewboard` — affected >=1.7 <1.7.10

## Details
Cross-site scripting (XSS) vulnerability in the auto-complete widget in htdocs/media/rb/js/reviews.js in Review Board 1.6.x before 1.6.17 and 1.7.x before 1.7.10 allows remote attackers to inject arbitrary web script or HTML via a full name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2209
- https://github.com/reviewboard/reviewboard/commit/4aaacbb1e628a80803ba1a55703db38fccdf7dbf
- https://bugzilla.redhat.com/show_bug.cgi?id=977423
- https://github.com/reviewboard/reviewboard
- http://www.openwall.com/lists/oss-security/2013/06/24/2
- http://www.reviewboard.org/docs/releasenotes/reviewboard/1.6.17
- http://www.reviewboard.org/docs/releasenotes/reviewboard/1.7.10
- http://www.reviewboard.org/news/2013/06/22/review-board-1617-and-1710-released
- http://www.tripwire.com/state-of-security/vulnerability-management/vulnerabilities-its-time-to-review-your-reviewboard
