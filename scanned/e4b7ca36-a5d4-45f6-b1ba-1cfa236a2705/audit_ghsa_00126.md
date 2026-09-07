# [H] Downloads Resources over HTTP in node-bsdiff-android

## Summary
Severity: High
Advisory: GHSA-c2vr-2c89-ph88
CVE: CVE-2016-10641
CWE: CWE-269, CWE-311
Ecosystem: npm
Published: 2018-09-18
Source: https://github.com/advisories/GHSA-c2vr-2c89-ph88
Type: github-advisory

## Affected
- npm: `node-bsdiff-android` — affected >=0

## Details
Affected versions of `node-bsdiff-android` insecurely download resources over HTTP. 

In scenarios where an attacker has a privileged network position, they can modify or read such resources at will. While the exact severity of impact for a vulnerability like this is highly variable and depends on the behavior of the package itself, it ranges from being able to read sensitive information all the way up to and including remote code execution.


## Recommendation

No patch is currently available for this vulnerability, and the package has not seen an update since 2014.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10641
- https://github.com/advisories/GHSA-c2vr-2c89-ph88
- https://github.com/arthur-zhang/node-bsdiff-android
- https://www.npmjs.com/advisories/234
