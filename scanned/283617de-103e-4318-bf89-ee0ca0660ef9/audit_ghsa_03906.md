# [H] Downloads Resources over HTTP in macaca-chromedriver-zxa

## Summary
Severity: High
Advisory: GHSA-3c87-r9f7-qfgq
CVE: CVE-2016-10623
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-3c87-r9f7-qfgq
Type: github-advisory

## Affected
- npm: `macaca-chromedriver-zxa` — affected >=0

## Details
Affected versions of `macaca-chromedriver-zxa` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `macaca-chromedriver-zxa`.


## Recommendation

The best mitigation is to manually set the download URL to a safe HTTPS server via the `CHROMEDRIVER_CDNURL` environment variable.

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10623
- https://github.com/advisories/GHSA-3c87-r9f7-qfgq
- https://www.npmjs.com/advisories/221
