# [C] Etherpad Lite Access Restriction Bypass

## Summary
Severity: Critical
Advisory: GHSA-mvmv-rq2j-97p2
CVE: CVE-2018-6835
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mvmv-rq2j-97p2
Type: github-advisory

## Affected
- npm: `ep_etherpad-lite` — affected >=0 <1.6.3

## Details
`node/hooks/express/apicalls.js` in Etherpad Lite before v1.6.3 mishandles JSONP, which allows remote attackers to bypass intended access restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6835
- https://github.com/ether/etherpad-lite/commit/626e58cc5af1db3691b41fca7b06c28ea43141b1
- https://github.com/ether/etherpad-lite
- https://github.com/ether/etherpad-lite/releases/tag/1.6.3
