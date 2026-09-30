# [M] HashiCorp Vault’s Microsoft SQL Database Storage Backend Vulnerable to SQL Injection Via Configuration File

## Summary
Severity: Medium
Advisory: GHSA-v3hp-mcj5-pg39
CVE: CVE-2023-0620
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-30
Source: https://github.com/advisories/GHSA-v3hp-mcj5-pg39
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.8.0 <1.11.9
- Go: `github.com/hashicorp/vault` — affected >=1.12.0 <1.12.5
- Go: `github.com/hashicorp/vault` — affected >=1.13.0 <1.13.1

## Details
HashiCorp Vault and Vault Enterprise versions 0.8.0 until 1.13.1 are vulnerable to an SQL injection attack when using the Microsoft SQL (MSSQL) Database Storage Backend. When configuring the MSSQL plugin, certain parameters are required to establish a connection (schema, database, and table) are not sanitized when passed to the user-provided MSSQL database. A privileged attacker with the ability to write arbitrary data to Vault's configuration may modify these parameters to execute a malicious SQL command when the Vault configuration is applied. This issue is fixed in versions 1.13.1, 1.12.5, and 1.11.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0620
- https://github.com/hashicorp/vault/pull/19591
- https://discuss.hashicorp.com/t/hcsec-2023-12-vault-s-microsoft-sql-database-storage-backend-vulnerable-to-sql-injection-via-configuration-file/52080/1
- https://github.com/hashicorp/vault
- https://github.com/hashicorp/vault/releases/tag/v1.11.9
- https://github.com/hashicorp/vault/releases/tag/v1.12.5
- https://github.com/hashicorp/vault/releases/tag/v1.13.1
- https://security.netapp.com/advisory/ntap-20230526-0008
