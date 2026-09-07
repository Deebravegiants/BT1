# [H] Clamscan vulnerable to command injection

## Summary
Severity: High
Advisory: GHSA-5v25-xr56-phph
CVE: CVE-2020-7613
CWE: CWE-74, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5v25-xr56-phph
Type: github-advisory

## Affected
- npm: `clamscan` — affected >=0 <1.3.0

## Details
clamscan through 1.2.0 is vulnerable to Command Injection. It is possible to inject arbitrary commands as part of the `_is_clamav_binary` function located within `Index.js`. It should be noted that this vulnerability requires a pre-requisite that a folder should be created with the same command that will be chained to execute. This lowers the risk of this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7613
- https://github.com/kylefarris/clamscan/pull/45
- https://github.com/kylefarris/clamscan/commit/5f557c970817fe8c578ec3f7ad3bcbcef4cf5538
- https://github.com/kylefarris/clamscan
- https://github.com/kylefarris/clamscan/blob/master/index.js#L34
- https://huntr.dev/bounties/1-npm-clamscan
- https://snyk.io/vuln/SNYK-JS-CLAMSCAN-564113
