# [H] SQL Injection in elide-datastore-aggregation

## Summary
Severity: High
Advisory: GHSA-8xpj-9j9g-fc9r
CVE: CVE-2022-24827
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-08
Source: https://github.com/advisories/GHSA-8xpj-9j9g-fc9r
Type: github-advisory

## Affected
- Maven: `com.yahoo.elide:elide-datastore-aggregation` — affected >=6.1.3 <6.1.4

## Details
### Impact
When leveraging the following together:

- Elide Aggregation Data Store for Analytic Queries
- Parameterized Columns (A column that requires a client provided parameter)
- A parameterized column of type TEXT

There is the potential for a hacker to provide a carefully crafted query that would bypass server side authorization filters through SQL injection.  A recent patch to Elide 6.1.2 allowed the '-' character to be included in parameterized TEXT columns.  This character can be interpreted as SQL comments ('--') and allow the attacker to remove the WHERE clause from the generated query and bypass authorization filters.

### Patches
A [fix](https://github.com/yahoo/elide/pull/2581) is provided in [Elide 6.1.4](https://github.com/yahoo/elide/releases/tag/6.1.4).

### Workarounds
The vulnerability only exists for parameterized columns of type TEXT and only for analytic queries (CRUD is not impacted).   Workarounds include leveraging a different type of parameterized column (TIME, MONEY, etc) or not leveraging parameterized columns.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [elide](https://github.com/yahoo/elide)
* Contact us in [Discord](https://discord.com/invite/3vh8ac57cc)

## References
- https://github.com/yahoo/elide/security/advisories/GHSA-8xpj-9j9g-fc9r
- https://nvd.nist.gov/vuln/detail/CVE-2022-24827
- https://github.com/yahoo/elide/pull/2581
- https://github.com/yahoo/elide
- https://github.com/yahoo/elide/releases/tag/6.1.4
