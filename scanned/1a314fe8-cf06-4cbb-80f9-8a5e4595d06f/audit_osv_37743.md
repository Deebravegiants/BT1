# [C] DataEase: SQL Injection in v2 Dataset Export

## Summary
Severity: Critical
Advisory: CVE-2026-33082
Aliases: GHSA-xxpw-2c8q-g693
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-33082
Type: osv

## Details
DataEase is an open source data visualization analysis tool. Versions 2.10.20 and below contain a SQL injection vulnerability in the dataset export functionality. The expressionTree parameter in POST /de2api/datasetTree/exportDataset is deserialized into a filtering object and passed to WhereTree2Str.transFilterTrees for SQL translation, where user-controlled values in "like" filter terms are directly concatenated into SQL fragments without sanitization. An attacker can inject arbitrary SQL commands by escaping the string literal in the filter value, enabling blind SQL injection through techniques such as time-based extraction of database information. This issue has been fixed in version 2.10.21.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33082.json
- https://github.com/dataease/dataease/security/advisories/GHSA-xxpw-2c8q-g693
- https://nvd.nist.gov/vuln/detail/CVE-2026-33082
