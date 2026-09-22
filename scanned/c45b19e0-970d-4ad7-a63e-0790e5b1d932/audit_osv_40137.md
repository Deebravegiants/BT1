# [M] DataEase: Remote Code Execution (RCE) via Zip Protocol & File Dropper

## Summary
Severity: Medium
Advisory: CVE-2026-50124
Aliases: GHSA-cjmg-jqmc-xj5v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-50124
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.23, DataEase can be exploited by uploading payload.zip through the Excel upload API /datasource/upload, creating an H2 datasource that uses the zip: protocol, and executing an SQL dataset path where CalciteProvider.jdbcFetchResultField calls statement.executeQuery(), causing precompiled Java aliases in test.mv.db to execute arbitrary code. This issue is fixed in version 2.10.23.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50124.json
- https://github.com/dataease/dataease/security/advisories/GHSA-cjmg-jqmc-xj5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-50124
- https://github.com/dataease/dataease/commit/304104d70e27a97f8909981f56209edc117dc285
- https://github.com/dataease/dataease/commit/a7bffa795cb0ca041dce0effe68479cf3bf13db1
