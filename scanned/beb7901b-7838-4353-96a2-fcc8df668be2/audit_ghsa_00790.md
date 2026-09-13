# [H] Unauthenticated Remote Command Injection in ep_imageconvert

## Summary
Severity: High
Advisory: GHSA-28gr-86hg-r48w
CVE: CVE-2013-3364
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-28gr-86hg-r48w
Type: github-advisory

## Affected
- npm: `ep_imageconvert` — affected >=0 <0.0.3

## Details
ep_imageconvert is a plugin for [Etherpad Lite](https://github.com/ether/etherpad-lite). ep_imageconvert <= 0.0.2 is vulnerable to remote command injection.

Authentication is not required for remote exploitation.


## Recommendation

Update to version 0.0.3 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-3364
- https://github.com/redhog/ep_imageconvert/pull/5
- https://github.com/redhog/ep_imageconvert
- https://snyk.io/vuln/npm:ep_imageconvert:20130506
- https://www.npmjs.com/advisories/7
