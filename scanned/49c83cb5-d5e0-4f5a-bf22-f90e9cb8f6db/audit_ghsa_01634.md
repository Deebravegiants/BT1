# [H] TaffyDB can allow access to any data items in the DB

## Summary
Severity: High
Advisory: GHSA-mxhp-79qh-mcx6
CVE: CVE-2019-10790
CWE: CWE-20, CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-02-19
Source: https://github.com/advisories/GHSA-mxhp-79qh-mcx6
Type: github-advisory

## Affected
- npm: `taffy` — affected >=0
- npm: `taffydb` — affected >=0

## Details
TaffyDB allows attackers to forge adding additional properties into user-input processed by taffy which can allow access to any data items in the DB. Taffy sets an internal index for each data item in its DB. However, it is found that the internal index can be forged by adding additional properties into user-input. If index is found in the query, TaffyDB will ignore other query conditions and directly return the indexed data item. Moreover, the internal index is in an easily-guessable format (e.g., T000002R000001). As such, attackers can use this vulnerability to access any data items in the DB. **Note:** `taffy` and its successor package `taffydb` are not maintained.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10790
- https://snyk.io/vuln/SNYK-JS-TAFFY-546521
- https://www.npmjs.com/package/taffy
- https://www.npmjs.com/package/taffydb
