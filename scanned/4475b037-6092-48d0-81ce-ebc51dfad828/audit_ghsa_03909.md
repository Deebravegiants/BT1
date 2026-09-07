# [H] SQL Injection in sequelize

## Summary
Severity: High
Advisory: GHSA-9c2p-jw8p-f84v
CVE: CVE-2016-10556
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-9c2p-jw8p-f84v
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <3.20.0

## Details
Affected versions of `sequelize` cast arrays to strings and fail to properly escape the resulting SQL statement, resulting in a SQL injection vulnerability.


## Proof of Concept
In Postgres, SQLite, and Microsoft SQL Server there is an issue where arrays are treated as strings and improperly escaped.

Example Query:
```
database.query('SELECT * FROM TestTable WHERE Name IN (:names)', {
  replacements: {
    names: directCopyOfUserInput
  }
});
```

If the user inputs the value of `:names` as:
```
["test", "'); DELETE TestTable WHERE Id = 1 --')"]
```

The resulting SQL statement will be:
```sql
SELECT Id FROM Table WHERE Name IN ('test', '\'); DELETE TestTable WHERE Id = 1 --')
```
As the backslash has no special meaning in PostgreSQL, MSSQL, or SQLite, the statement will delete the record in TestTable with an Id of 1.


## Recommendation

Update to version 3.20.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10556
- https://github.com/sequelize/sequelize/issues/5671
- https://github.com/sequelize/sequelize/commit/23952a2b020cc3571f090e67dae7feb084e1be71
- https://github.com/sequelize/sequelize/commits/v3.20.0?after=62e4dacb28a779a190a3e042b971dcd8c7926e49+34&branch=v3.20.0&qualified_name=refs%2Ftags%2Fv3.20.0
