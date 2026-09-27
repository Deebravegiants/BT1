# [C] DataEase: RCE Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-45534
Aliases: GHSA-cv4c-8rpv-2x97
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-45534
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.23, DataEase Redshift datasource connections can load attacker-controlled rsjdbc.ini configuration from System.getProperty("java.io.tmpdir"), setting socketFactory=org.springframework.context.support.FileSystemXmlApplicationContext so com.amazon.redshift.Driver#connect, com.amazon.redshift.Driver#getJdbcIniFile, and com.amazon.redshift.util.ObjectFactory#instantiate execute a reflection-based remote code execution chain during a normal JDBC connection through io.dataease.datasource.type.Redshift. This issue is fixed in version 2.10.23.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45534.json
- https://github.com/dataease/dataease/security/advisories/GHSA-cv4c-8rpv-2x97
- https://nvd.nist.gov/vuln/detail/CVE-2026-45534
- https://github.com/dataease/dataease/commit/3e58149f1e014b1a7ae2c12134b37ae438f676ac
