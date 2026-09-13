# [H] ipip-coffee downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-m8pw-h8qj-rgj9
CVE: CVE-2016-10673
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-m8pw-h8qj-rgj9
Type: github-advisory

## Affected
- npm: `ipip-coffee` — affected >=0

## Details
Affected versions of `ipip-coffee` insecurely download resources over HTTP. 

In scenarios where an attacker has a privileged network position, they can modify or read such resources at will. This could impact the integrity and availability of the data being used to make geolocation decisions by an application.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10673
- https://github.com/advisories/GHSA-m8pw-h8qj-rgj9
- https://www.npmjs.com/advisories/279
