# [M] DuckDB AWS Extension Security Policy Bypass via load_aws_credentials Procedure

## Summary
Severity: Medium
Advisory: CVE-2026-58139
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-58139
Type: osv

## Details
The DuckDB AWS extension for DuckDB contains a security policy bypass vulnerability that allows any database user with SQL execution permissions to extract plaintext AWS credentials by calling the load_aws_credentials function with the redact_secret parameter set to false, circumventing the database-wide allow_unredacted_secrets=false policy. Attackers can invoke this single function to retrieve the underlying AWS credential chain including access_key_id, secret_access_key, session_token, and region in plaintext, which are immediately valid against AWS APIs and particularly impactful in managed environments where pg_duckdb is preloaded and an AWS credential chain such as IMDSv2, IRSA, ECS task role, or EC2 instance role is reachable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58139.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58139
- https://www.vulncheck.com/advisories/duckdb-aws-extension-security-policy-bypass-via-load-aws-credentials-procedure
- https://github.com/duckdb/duckdb-aws/pull/156
- https://github.com/duckdb/duckdb-aws/commit/7d04119ee8d3f8836e278f0e8cbf21827ff5338b
- https://github.com/duckdb/duckdb-aws
