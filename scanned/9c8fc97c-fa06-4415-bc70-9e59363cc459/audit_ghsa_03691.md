# [C] Sandbox Bypass Leading to Arbitrary Code Execution in constantinople

## Summary
Severity: Critical
Advisory: GHSA-4vmm-mhcq-4x9j
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2019-06-14
Source: https://github.com/advisories/GHSA-4vmm-mhcq-4x9j
Type: github-advisory

## Affected
- npm: `constantinople` — affected >=0 <3.1.1

## Details
Versions of `constantinople` prior to 3.1.1 are vulnerable to a sandbox bypass which can lead to arbitrary code execution.


## Recommendation

Update to version 3.1.1 or later.

## References
- https://github.com/pugjs/constantinople/commit/01d409c0d081dfd65223e6b7767c244156d35f7f
- https://bugzilla.redhat.com/show_bug.cgi?id=1577703
- https://snyk.io/vuln/npm:constantinople:20180421
- https://www.npmjs.com/advisories/568
