# [C] Sequelize vulnerable to SQL Injection via replacements

## Summary
Severity: Critical
Advisory: GHSA-wrh9-cjv3-2hpw
CVE: CVE-2023-25813
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-22
Source: https://github.com/advisories/GHSA-wrh9-cjv3-2hpw
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <6.19.1

## Details
### Impact

The SQL injection exploit is related to replacements. Here is such an example: 

In the following query, some parameters are passed through replacements, and some are passed directly through the `where` option.

```typescript
User.findAll({
  where: or(
    literal('soundex("firstName") = soundex(:firstName)'),
    { lastName: lastName },
  ),
  replacements: { firstName },
})
```

This is a very legitimate use case, but this query was vulnerable to SQL injection due to how Sequelize processed the query: Sequelize built a first query using the `where` option, then passed it over to `sequelize.query` which parsed the resulting SQL to inject all `:replacements`.

If the user passed values such as

```json
{
  "firstName": "OR true; DROP TABLE users;",
  "lastName": ":firstName"
}
```

Sequelize would first generate this query:

```sql
SELECT * FROM users WHERE soundex("firstName") = soundex(:firstName) OR "lastName" = ':firstName'
```

Then would inject replacements in it, which resulted in this:

```sql
SELECT * FROM users WHERE soundex("firstName") = soundex('OR true; DROP TABLE users;') OR "lastName" = ''OR true; DROP TABLE users;''
```

As you can see this resulted in arbitrary user-provided SQL being executed.

### Patches

The issue was fixed in Sequelize 6.19.1

### Workarounds

Do not use the `replacements` and the `where` option in the same query if you are not using Sequelize >= 6.19.1 

### References

See this thread for more information: https://github.com/sequelize/sequelize/issues/14519

Snyk: https://security.snyk.io/vuln/SNYK-JS-SEQUELIZE-2932027

## References
- https://github.com/sequelize/sequelize/security/advisories/GHSA-wrh9-cjv3-2hpw
- https://nvd.nist.gov/vuln/detail/CVE-2023-25813
- https://github.com/sequelize/sequelize/issues/14519
- https://github.com/sequelize/sequelize/commit/ccaa3996047fe00048d5993ab2dd43ebadd4f78b
- https://github.com/sequelize/sequelize
- https://github.com/sequelize/sequelize/releases/tag/v6.19.1
- https://security.snyk.io/vuln/SNYK-JS-SEQUELIZE-2932027
