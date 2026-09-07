# [M] Cross-site Scripting in peertube

## Summary
Severity: Medium
Advisory: GHSA-f2c5-997w-7f5c
CVE: CVE-2021-3780
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-f2c5-997w-7f5c
Type: github-advisory

## Affected
- npm: `peertube` — affected >=0 <3.4.0

## Details
peertube is vulnerable to Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting'). It was found that one could upload a SVG image and then send the url of that to other users and when they open the link we can get their complete session keys as the session keys stored in local storage and with Javascript easily can be stolen by attackers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3780
- https://github.com/chocobozzz/peertube/commit/0ea2f79d45b301fcd660efc894469a99b2239bf6
- https://github.com/chocobozzz/peertube
- https://huntr.dev/bounties/282807a8-4bf5-4fe2-af62-e05f945b3d65
