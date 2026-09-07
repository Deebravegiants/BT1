# [M] studygolang vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-gw62-c7w4-x449
CVE: CVE-2021-4272
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-21
Source: https://github.com/advisories/GHSA-gw62-c7w4-x449
Type: github-advisory

## Affected
- Go: `github.com/studygolang/studygolang` — affected >=0

## Details
A vulnerability classified as problematic has been found in studygolang. This affects an unknown part of the file static/js/topics.js. The manipulation of the argument contentHtml leads to cross site scripting. It is possible to initiate the attack remotely. The name of the patch is 0fb30f9640bd5fa0cae58922eac6c00bb1a94391. It is recommended to apply a patch to fix this issue. The identifier VDB-216477 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4272
- https://github.com/studygolang/studygolang/commit/0fb30f9640bd5fa0cae58922eac6c00bb1a94391
- https://github.com/studygolang/studygolang
- https://vuldb.com/?id.216477
