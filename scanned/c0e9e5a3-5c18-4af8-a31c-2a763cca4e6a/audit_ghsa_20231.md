# [H] OS Command Injection in git-promise

## Summary
Severity: High
Advisory: GHSA-chj3-f7xw-367m
CVE: CVE-2022-24376
CWE: CWE-77, CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-11
Source: https://github.com/advisories/GHSA-chj3-f7xw-367m
Type: github-advisory

## Affected
- npm: `git-promise` — affected >=0

## Details
All versions of package git-promise is vulnerable to Command Injection due to an inappropriate fix of a prior [vulnerability](https://security.snyk.io/vuln/SNYK-JS-GITPROMISE-567476) in this package. **Note:** Please note that the vulnerability will not be fixed. The README file was updated with a warning regarding this issue. 
### Credits
 @lirantal for discovering this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24376
- https://github.com/lirantal/git-promise/commit/030e4f993f3b65419d60f7f60e81e0a742b72e77
- https://gist.github.com/lirantal/9da1fceb32f5279eb76a5fc1cb9707dd
- https://github.com/piuccio/git-promise
- https://snyk.io/vuln/SNYK-JS-GITPROMISE-2434310
