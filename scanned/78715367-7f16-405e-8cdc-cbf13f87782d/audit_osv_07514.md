# [H] BIT-sqlite-2026-51302

## Summary
Severity: High
Advisory: BIT-sqlite-2026-51302
Aliases: CVE-2026-51302
Ecosystem: Bitnami
Published: 2026-07-30
Source: https://osv.dev/vulnerability/BIT-sqlite-2026-51302
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.41.0

## Details
SQLite 3.41 has a use-after-free vulnerability exists in the expression evaluation logic. The sqlite3ReleaseTempReg function improperly releases temporary register resources, and the subsequent exprComputeOperands function continues to access the already freed register memory. By supplying a malicious SQL statement, a remote attacker can exploit this flaw to cause denial of service, leak sensitive information, or potentially execute arbitrary code on the affected system.

## References
- https://github.com/programmervuln/cveadvisory-/blob/main/CVE-2026-51302
- https://github.com/sqlite/sqlite/blob/master/src/expr.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-51302
