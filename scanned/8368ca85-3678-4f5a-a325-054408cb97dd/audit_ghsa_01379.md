# [H] gfe-sass downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-72q2-5rxx-xfff
CVE: CVE-2017-16040
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-72q2-5rxx-xfff
Type: github-advisory

## Affected
- npm: `gfe-sass` — affected >=0.0.0

## Details
Affected versions of `gfe-sass` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `gfe-sass`.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16040
- https://www.npmjs.com/advisories/291
