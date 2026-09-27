# [H] Downloads Resources over HTTP in openframe-glslviewer

## Summary
Severity: High
Advisory: GHSA-g2pf-qjgf-6fw3
CVE: CVE-2016-10607
CWE: CWE-269, CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-g2pf-qjgf-6fw3
Type: github-advisory

## Affected
- npm: `openframe-glslviewer` — affected >=0

## Details
Affected versions of `openframe-glslviewer` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `openframe-glslviewer`.


## Recommendation

No patch is currently available for this vulnerability, and the package hasn't been updated since 2014.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10607
- https://github.com/OpenframeProject/Openframe-glslViewer
- https://github.com/advisories/GHSA-g2pf-qjgf-6fw3
- https://www.npmjs.com/advisories/208
