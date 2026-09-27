# [H] Downloads Resources over HTTP in atom-node-module-installer

## Summary
Severity: High
Advisory: GHSA-87g3-x896-w798
CVE: CVE-2016-10620
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-87g3-x896-w798
Type: github-advisory

## Affected
- npm: `atom-node-module-installer` — affected >=0

## Details
Affected versions of `atom-node-module-installer` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `atom-node-module-installer`.


## Recommendation

No patch is currently available for this vulnerability, and the package has not been updated since 2014.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10620
- https://github.com/advisories/GHSA-87g3-x896-w798
- https://www.npmjs.com/advisories/216
