# [H] AWS Advanced Go Wrapper has Privilege Escalation in Aurora PostgreSQL instance

## Summary
Severity: High
Advisory: GHSA-r236-5pc3-3qcp
CVE: CVE-2026-11401
CWE: CWE-426
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-r236-5pc3-3qcp
Type: github-advisory

## Affected
- Go: `github.com/aws/aws-advanced-go-wrapper/awssql/v2` — affected >=0 <2.0.1
- Go: `github.com/aws/aws-advanced-go-wrapper/xray` — affected >=0 <1.07
- Go: `github.com/aws/aws-advanced-go-wrapper/aws-secrets-manager` — affected >=0 <1.1.2
- Go: `github.com/aws/aws-advanced-go-wrapper/custom-endpoint` — affected >=0 <1.0.4
- Go: `github.com/aws/aws-advanced-go-wrapper/federated-auth` — affected >=0 <1.1.1
- Go: `github.com/aws/aws-advanced-go-wrapper/iam` — affected >=0 <1.1.1
- Go: `github.com/aws/aws-advanced-go-wrapper/mysql-driver` — affected >=0 <1.1.1
- Go: `github.com/aws/aws-advanced-go-wrapper/okta` — affected >=0 <1.1.1
- Go: `github.com/aws/aws-advanced-go-wrapper/pgx-driver` — affected >=0 <1.1.1
- Go: `github.com/aws/aws-advanced-go-wrapper/otlp` — affected >=0 <1.0.7
- Go: `github.com/aws/aws-advanced-go-wrapper/auth-helpers` — affected >=0 <1.1.1

## Details
Aurora PostgreSQL is a fully managed relational database engine that's compatible with PostgreSQL.

An issue in Aurora PostgreSQL using the AWS Go Wrapper waa identified, see CVE-2026-11401.


Impact
An issue in AWS Wrappers for Amazon Aurora PostgreSQL may allow for privilege escalation to rds_superuser role. A low privilege authenticated user can create a crafted function that could be executed with permissions of other Amazon Relational Database Service (RDS) users.

Impacted versions: AWS Go Wrapper 2026-04-06

Patches
This issue has been addressed in  AWS Go Wrapper 2026-05-26. Maintainers recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

Workarounds
Remove the public schema from the search path.

References
If there are any questions or comments about this advisory, contact [AWS/Amazon] Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/aws-advanced-go-wrapper/security/advisories/GHSA-r236-5pc3-3qcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-11401
- https://aws.amazon.com/security/security-bulletins/2026-039-aws
- https://github.com/aws/aws-advanced-go-wrapper
- https://github.com/aws/aws-advanced-go-wrapper/releases/tag/release-2026-05-26
