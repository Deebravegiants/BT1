# [H] slimerjs-edge downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-5rc6-2r3r-fv79
CVE: CVE-2016-10644
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-15
Source: https://github.com/advisories/GHSA-5rc6-2r3r-fv79
Type: github-advisory

## Affected
- npm: `slimerjs-edge` — affected >=0

## Details
Affected versions of `slimerjs-edge` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `slimerjs-edge`.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10644
- https://github.com/advisories/GHSA-5rc6-2r3r-fv79
- https://www.npmjs.com/advisories/243
