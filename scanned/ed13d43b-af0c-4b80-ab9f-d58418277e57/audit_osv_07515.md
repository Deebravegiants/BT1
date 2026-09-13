# [H] BIT-sqlite-2026-51304

## Summary
Severity: High
Advisory: BIT-sqlite-2026-51304
Aliases: CVE-2026-51304
Ecosystem: Bitnami
Published: 2026-07-30
Source: https://osv.dev/vulnerability/BIT-sqlite-2026-51304
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.41.0

## Details
sqlite 3.41 has a use-after-free (UAF) vulnerability in the ORDER BY clause parsing routine. The affected code first releases the memory of an ExprList object via sqlite3ExprListDelete(), then attempts to access the nExpr member of the already freed object. This dangling pointer access causes invalid memory read operations. By constructing a malicious SQL statement containing an ORDER BY clause with a large number of items, a remote adversary can trigger this vulnerability. Successful exploitation can result in application crash (denial of service), leakage of sensitive memory contents, and under certain memory layout conditions, arbitrary code execution on the affected system.

## References
- https://github.com/programmervuln/cveadvisory-/blob/main/CVE-2026-51304
- https://github.com/sqlite/sqlite/blob/master/src/expr.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-51304
