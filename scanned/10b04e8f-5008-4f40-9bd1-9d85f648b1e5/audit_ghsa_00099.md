# [H] Downloads Resources over HTTP in cmake

## Summary
Severity: High
Advisory: GHSA-4j59-hfw6-6w7h
CVE: CVE-2016-10642
CWE: CWE-269, CWE-311
Ecosystem: npm
Published: 2018-08-15
Source: https://github.com/advisories/GHSA-4j59-hfw6-6w7h
Type: github-advisory

## Affected
- npm: `cmake` — affected >=0

## Details
Affected versions of `cmake` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `cmake`.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different package if available, or installing the cmake binaries via a system package manager, such as `apt-get`.

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10642
- https://github.com/advisories/GHSA-4j59-hfw6-6w7h
- https://github.com/stanley-gu/cmake
- https://www.npmjs.com/advisories/233
