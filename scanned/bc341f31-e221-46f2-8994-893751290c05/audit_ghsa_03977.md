# [H] appium-chromedriver downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-hc94-2wfr-4pwf
CVE: CVE-2016-10557
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-hc94-2wfr-4pwf
Type: github-advisory

## Affected
- npm: `appium-chromedriver` — affected >=0 <2.9.4

## Details
Affected versions of `appium-chromedriver` insecurely download resources over HTTP. 

In scenarios where an attacker has a privileged network position, they can modify or read items send over HTTP at will. In this case, that includes the chromedriver binary, which may result in remote code execution if overwritten with a malicious binary.


## Recommendation

Update to version 2.9.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10557
- https://github.com/advisories/GHSA-hc94-2wfr-4pwf
- https://www.npmjs.com/advisories/162
