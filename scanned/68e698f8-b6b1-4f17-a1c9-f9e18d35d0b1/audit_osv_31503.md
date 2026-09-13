# [C] CVE-2025-12967

## Summary
Severity: Critical
Advisory: CVE-2025-12967
Aliases: GHSA-4jvf-wx3f-2x8q, PYSEC-2026-1205
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-10
Source: https://osv.dev/vulnerability/CVE-2025-12967
Type: osv

## Details
An issue in AWS Wrappers for Amazon Aurora PostgreSQL may allow for privilege escalation to rds_superuser role. A low privilege authenticated user can create a crafted function that could be executed with permissions of other Amazon Relational Database Service (RDS) users.

We recommend customers upgrade to the following versions: AWS JDBC Wrapper to v2.6.5, AWS Go Wrapper to 2025-10-17, AWS NodeJS Wrapper to v2.0.1, AWS Python Wrapper to v1.4.0 and AWS PGSQL ODBC driver to v1.0.1

## References
- https://aws.amazon.com/security/security-bulletins/AWS-2025-028/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12967.json
- https://github.com/aws/aws-advanced-go-wrapper/security/advisories/GHSA-7wq2-32h4-9hc9
- https://github.com/aws/aws-advanced-jdbc-wrapper/security/advisories/GHSA-7xw4-g7mm-r4hh
- https://github.com/aws/aws-advanced-nodejs-wrapper/security/advisories/GHSA-8wj8-cfxr-9374
- https://github.com/aws/aws-advanced-python-wrapper/security/advisories/GHSA-4jvf-wx3f-2x8q
- https://github.com/aws/aws-pgsql-odbc/security/advisories/GHSA-q327-fgm8-7mxf
- https://nvd.nist.gov/vuln/detail/CVE-2025-12967
- https://github.com/aws/aws-advanced-go-wrapper/releases/tag/release-2025-10-17
- https://github.com/aws/aws-advanced-jdbc-wrapper/releases/tag/2.6.5
- https://github.com/aws/aws-advanced-nodejs-wrapper/releases/tag/2.0.1
- https://github.com/aws/aws-advanced-python-wrapper/releases/tag/1.4.0
- https://github.com/aws/aws-pgsql-odbc/releases/tag/1.0.1
