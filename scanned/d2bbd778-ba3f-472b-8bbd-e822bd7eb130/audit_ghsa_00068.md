# [H] Downloads Resources over HTTP in haxe3

## Summary
Severity: High
Advisory: GHSA-2r9c-46v3-43fc
CVE: CVE-2016-10688
CWE: CWE-311
Ecosystem: npm
Published: 2018-08-17
Source: https://github.com/advisories/GHSA-2r9c-46v3-43fc
Type: github-advisory

## Affected
- npm: `haxe3` — affected >=0

## Details
Affected versions of `haxe3` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `haxe3`.


## Recommendation

No patch is currently available for this vulnerability. This vulnerability has been left unpatched for several years, despite active maintenance on the package. Because of this, it appears that the package author has accepted the risk, and is unlikely to patch this package in the future.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10688
- https://github.com/advisories/GHSA-2r9c-46v3-43fc
- https://www.npmjs.com/advisories/294
