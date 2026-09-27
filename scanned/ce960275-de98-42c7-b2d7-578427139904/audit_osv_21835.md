# [M] CVE-2021-47714

## Summary
Severity: Medium
Advisory: CVE-2021-47714
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2021-47714
Type: osv

## Details
Hasura GraphQL 1.3.3 contains a local file read vulnerability that allows attackers to access system files through SQL injection in the query endpoint. Attackers can exploit the pg_read_file() PostgreSQL function by crafting malicious SQL queries to read arbitrary files on the server.

## References
- https://github.com/hasura/graphql-engine
- https://www.exploit-db.com/exploits/49790
- https://www.vulncheck.com/advisories/hasura-graphql-local-file-read-via-sql-injection
