# [C] SQLite integer overflow in key info allocation may lead to information disclosure.

## Summary
Severity: Critical
Advisory: BIT-sqlite-2025-7458
Aliases: CVE-2025-7458
Ecosystem: Bitnami
Published: 2025-07-31
Source: https://osv.dev/vulnerability/BIT-sqlite-2025-7458
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.39.2 <3.41.2

## Details
An integer overflow in the sqlite3KeyInfoFromExprList function in SQLite versions 3.39.2 through 3.41.1 allows an attacker with the ability to execute arbitrary SQL statements to cause a denial of service or disclose sensitive information from process memory via a crafted SELECT statement with a large number of expressions in the ORDER BY clause.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-7458
- https://sqlite.org/forum/forumpost/16ce2bb7a639e29b
- https://sqlite.org/src/info/12ad822d9b827777
