# [C] PraisonAI before 4.6.78 SQL/CQL Injection via vector dimension

## Summary
Severity: Critical
Advisory: CVE-2026-60090
Aliases: GHSA-wf65-4jjx-q444
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/CVE-2026-60090
Type: osv

## Details
PraisonAI before 4.6.78 fails to validate the caller-controlled dimension argument in the PGVector and Cassandra knowledge-store create_collection() backends. Although schema, keyspace, and collection-name identifiers are validated, the dimension value (declared as int but not enforced at runtime) is interpolated directly into the vector column of the generated CREATE TABLE DDL. A caller able to influence collection-creation dimensions can pass a string such as '3); DROP TABLE tenant_secrets; --' to inject SQL/CQL tokens into the statement executed by the database driver.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60090.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-wf65-4jjx-q444
- https://nvd.nist.gov/vuln/detail/CVE-2026-60090
- https://www.vulncheck.com/advisories/praisonai-before-sql-cql-injection-via-vector-dimension
- https://github.com/MervinPraison/PraisonAI/commit/3aa9cbc2bd49c23a32be0a89a5e620d13d843eab
