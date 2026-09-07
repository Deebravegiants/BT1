# [H] fis-sass-all downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-vcfp-ppqw-mf23
CVE: CVE-2016-10686
CWE: CWE-269, CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-17
Source: https://github.com/advisories/GHSA-vcfp-ppqw-mf23
Type: github-advisory

## Affected
- npm: `fis-sass-all` — affected >=0

## Details
Affected versions of `fis-sass-all` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `fis-sass-all`.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different package if available. 

Alternatively, the risk of exploitation can be reduced by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10686
- https://github.com/advisories/GHSA-vcfp-ppqw-mf23
- https://github.com/fis-dev/fis-sass
- https://www.npmjs.com/advisories/287
