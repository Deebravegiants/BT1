# [H] CVE-2022-25860

## Summary
Severity: High
Advisory: CVE-2022-25860
Aliases: GHSA-9w5j-4mwv-2wj8
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H/E:P)
Published: 2023-01-24
Source: https://osv.dev/vulnerability/CVE-2022-25860
Type: osv

## Details
Versions of the package simple-git before 3.16.0 are vulnerable to Remote Code Execution (RCE) via the clone(), pull(), push() and listRemote() methods, due to improper input sanitization.This vulnerability exists due to an incomplete fix of [CVE-2022-25912](https://security.snyk.io/vuln/SNYK-JS-SIMPLEGIT-3112221).

## References
- https://github.com/steveukx/git-js/pull/881/commits/95459310e5b8f96e20bb77ef1a6559036b779e13
- https://security.snyk.io/vuln/SNYK-JS-SIMPLEGIT-3177391
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/25xxx/CVE-2022-25860.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-25860
- https://github.com/steveukx/git-js/commit/ec97a39ab60b89e870c5170121cd9c1603cc1951
