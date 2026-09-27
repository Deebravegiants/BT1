# [M] Downloads Resources over HTTP in jser-stat

## Summary
Severity: Medium
Advisory: GHSA-5w4p-h4gm-3w26
CVE: CVE-2016-10592
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-5w4p-h4gm-3w26
Type: github-advisory

## Affected
- npm: `jser-stat` — affected >=0

## Details
Affected versions of `jser-stat` insecurely downloads resources over HTTP. 

In scenarios where an attacker has a privileged network position, they can modify or read such resources at will. While the exact severity of impact for a vulnerability like this is highly variable and depends on the behavior of the package itself, it ranges from being able to read sensitive information all the way up to and including remote code execution.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10592
- https://github.com/advisories/GHSA-5w4p-h4gm-3w26
- https://github.com/jser/stat-js/blob/master/data/url-mapping.js
- https://www.npmjs.com/advisories/188
