# [M] Downloads Resources over HTTP in adamvr-geoip-lite

## Summary
Severity: Medium
Advisory: GHSA-h2jv-5v3f-7m7j
CVE: CVE-2016-10680
CWE: CWE-311
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-h2jv-5v3f-7m7j
Type: github-advisory

## Affected
- npm: `adamvr-geoip-lite` — affected >=0.0.0

## Details
Affected versions of `adamvr-geoip-lite` insecurely download resources over HTTP. 

In scenarios where an attacker has a privileged network position, they can modify or read such resources at will. This could impact the integrity and availability of the data being used to make geolocation decisions by an application.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10680
- https://www.npmjs.com/advisories/283
