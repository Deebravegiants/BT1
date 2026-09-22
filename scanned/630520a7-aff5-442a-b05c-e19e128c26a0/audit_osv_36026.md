# [C] MongoDB BI Connector ODBC driver may write outside an allocated buffer when the setup dialog opens a data source with oversized path settings

## Summary
Severity: Critical
Advisory: CVE-2026-19003
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-19003
Type: osv

## Details
A data source definition containing an over-length file path setting may cause the MongoDB BI Connector ODBC Driver setup dialog to write outside the bounds of an allocated buffer. The issue stems from an incorrect buffer capacity calculation in the dialog's file and folder selection handling, and is reached only when a user opens the setup dialog for such a data source and initiates a file or folder selection. Depending on build configuration, the result may range from abnormal process termination to, under certain conditions, execution of unintended code in the context of the user running the dialog.

## References
- https://github.com/mongodb/mongo-bi-connector-odbc-driver/releases/tag/v1.4.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19003.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19003
- https://github.com/mongodb/mongo-bi-connector-odbc-driver
