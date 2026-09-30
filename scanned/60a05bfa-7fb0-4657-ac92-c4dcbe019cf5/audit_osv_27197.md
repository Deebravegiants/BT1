# [C] SQL Injection in the Amazon Redshift ODBC Driver affecting v2.1.5.0

## Summary
Severity: Critical
Advisory: CVE-2024-12746
Aliases: GHSA-g63m-5vjv-wr3v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-12746
Type: osv

## Details
A SQL injection in the Amazon Redshift ODBC Driver v2.1.5.0 (Windows or Linux) allows a user to gain escalated privileges via the SQLTables or SQLColumns Metadata APIs. Users are recommended to upgrade to the driver version 2.1.6.0 or revert to driver version 2.1.4.0.

## References
- https://aws.amazon.com/security/security-bulletins/AWS-2024-015/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12746.json
- https://github.com/aws/amazon-redshift-odbc-driver/security/advisories/GHSA-g63m-5vjv-wr3v
- https://nvd.nist.gov/vuln/detail/CVE-2024-12746
- https://github.com/aws/amazon-redshift-odbc-driver/releases/tag/v2.1.6
- https://github.com/aws/amazon-redshift-odbc-driver
