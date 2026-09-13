# [H] Amazon Redshift JDBC Driver vulnerable to SQL Injection

## Summary
Severity: High
Advisory: GHSA-8596-2jgr-ppj7
CVE: CVE-2024-12744
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-26
Source: https://github.com/advisories/GHSA-8596-2jgr-ppj7
Type: github-advisory

## Affected
- Maven: `com.amazon.redshift:redshift-jdbc42` — affected >=2.1.0.31 <2.1.0.32

## Details
### Summary
A SQL injection in the Amazon Redshift JDBC Driver in v2.1.0.31 allows a user to gain escalated privileges via schema injection in the getSchemas, getTables, or getColumns Metadata APIs. Users should upgrade to the driver version 2.1.0.32 or revert to driver version 2.1.0.30.

### Impact
A SQL injection is possible in the Amazon Redshift JDBC Driver, version 2.1.0.31, when leveraging metadata APIs to retrieve information about database schemas, tables, or columns.

**Impacted versions:** Amazon Redshift JDBC Driver version 2.1.0.31.

### Patches
The issue described above has been addressed in the Amazon Redshift JDBC Driver, version 2.1.0.32.

The patch implemented in this version ensures that every metadata command input is sent to the Redshift server as part of a parameterized query, using either QUOTE_IDENT(string) or QUOTE_LITERAL(string). After processing all the inputs into quoted identifiers or literals, the metadata command is composed using these inputs and then executed on the server.

### Workarounds
Use the previous version of the Amazon Redshift JDBC Driver, 2.1.0.30.

### References
If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page [1] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

[1] Vulnerability reporting page: https://aws.amazon.com/security/vulnerability-reporting

## References
- https://github.com/aws/amazon-redshift-jdbc-driver/security/advisories/GHSA-8596-2jgr-ppj7
- https://nvd.nist.gov/vuln/detail/CVE-2024-12744
- https://aws.amazon.com/security/security-bulletins/AWS-2024-015
- https://github.com/aws/amazon-redshift-jdbc-driver
- https://github.com/aws/amazon-redshift-jdbc-driver/releases/tag/v2.1.0.32
