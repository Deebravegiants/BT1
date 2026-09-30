# [H] Downloads Resources over HTTP in grunt-webdriver-qunit

## Summary
Severity: High
Advisory: GHSA-4q79-fch7-g78q
CVE: CVE-2016-10606
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-4q79-fch7-g78q
Type: github-advisory

## Affected
- npm: `grunt-webdriver-qunit` — affected >=0

## Details
Affected versions of `grunt-webdriver-qunit` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `grunt-webdriver-qunit`.


## Recommendation

No patch is currently available for this vulnerability, and the package author has marked the package as deprecated.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10606
- https://github.com/advisories/GHSA-4q79-fch7-g78q
- https://www.npmjs.com/advisories/207
