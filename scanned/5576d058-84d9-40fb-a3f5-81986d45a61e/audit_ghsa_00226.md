# [H] hubl-server downloads resources over HTTP

## Summary
Severity: High
Advisory: GHSA-h8mc-42c3-r72p
CVE: CVE-2017-16035
CWE: CWE-311
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-h8mc-42c3-r72p
Type: github-advisory

## Affected
- npm: `hubl-server` — affected >=0

## Details
Affected versions of `hubl-server` insecurely download dependencies over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the responses and replace the dependencies with malicious ones, resulting in code execution on the system running `hubl-server`.


## Recommendation

No patch is currently available for this vulnerability, and it has not seen any updates since 2015.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised yo

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16035
- https://github.com/advisories/GHSA-h8mc-42c3-r72p
- https://www.npmjs.com/advisories/334
