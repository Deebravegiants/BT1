# [H] clang-extra downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-59m2-j944-839w
CVE: CVE-2016-10655
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-59m2-j944-839w
Type: github-advisory

## Affected
- npm: `clang-extra` — affected >=0

## Details
Affected versions of `clang-extra` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `clang-extra`.


## Recommendation

No patch is currently available for this vulnerability. The package author stated that no patch is possible until llvm provides HTTPS support, and a patch would be possible if that ever happened in the future.

The best mitigation option is to reduce the risk of exploitation as much as possible. This can be done by ensuring that this package is not installed while connected to a public network. If the package is installed on a private network, the only people who can exploit this vulnerability are those who have compromised your network or those who have privileged access to your ISP, such as Nation State Actors or Rogue ISP Employees.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10655
- https://github.com/advisories/GHSA-59m2-j944-839w
- https://www.npmjs.com/advisories/265
