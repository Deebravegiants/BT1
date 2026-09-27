# [H] Downloads Resources over HTTP in haxeshim

## Summary
Severity: High
Advisory: GHSA-cr6c-85fh-cqpg
CVE: CVE-2016-10692
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-cr6c-85fh-cqpg
Type: github-advisory

## Affected
- npm: `haxeshim` — affected >=0

## Details
Affected versions of `haxeshim` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `haxeshim`.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10692
- https://github.com/advisories/GHSA-cr6c-85fh-cqpg
- https://www.npmjs.com/advisories/300
