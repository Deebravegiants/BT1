# [H] Remote Code Execution (RCE)

## Summary
Severity: High
Advisory: CVE-2022-25912
Aliases: GHSA-9p95-fxvg-qgq2
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H/E:P)
Published: 2022-12-06
Source: https://osv.dev/vulnerability/CVE-2022-25912
Type: osv

## Details
The package simple-git before 3.15.0 are vulnerable to Remote Code Execution (RCE) when enabling the ext transport protocol, which makes it exploitable via clone() method. This vulnerability exists due to an incomplete fix of [CVE-2022-24066](https://security.snyk.io/vuln/SNYK-JS-SIMPLEGIT-2434306).

## References
- https://github.com/steveukx/git-js/blob/main/docs/PLUGIN-UNSAFE-ACTIONS.md%23overriding-allowed-protocols
- https://github.com/steveukx/git-js/releases/tag/simple-git%403.15.0
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-3153532
- https://security.snyk.io/vuln/SNYK-JS-SIMPLEGIT-3112221
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/25xxx/CVE-2022-25912.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-25912
- https://github.com/steveukx/git-js/commit/774648049eb3e628379e292ea172dccaba610504
