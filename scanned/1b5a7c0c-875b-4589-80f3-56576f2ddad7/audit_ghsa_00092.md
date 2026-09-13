# [H] Downloads Resources over HTTP in resourcehacker

## Summary
Severity: High
Advisory: GHSA-p65h-233c-jxvm
CVE: CVE-2016-10646
CWE: CWE-311
Ecosystem: npm
Published: 2018-08-15
Source: https://github.com/advisories/GHSA-p65h-233c-jxvm
Type: github-advisory

## Affected
- npm: `resourcehacker` — affected >=0

## Details
Affected versions of `resourcehacker` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `resourcehacker`.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10646
- https://github.com/advisories/GHSA-p65h-233c-jxvm
- https://github.com/felicienfrancois/node-resourcehacker/blob/master/scripts/install.js#L4
- https://www.npmjs.com/advisories/254
