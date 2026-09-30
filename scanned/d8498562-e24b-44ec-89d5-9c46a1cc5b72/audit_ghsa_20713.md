# [H] PostgreSQL JDBC Driver SQL Injection in ResultSet.refreshRow() with malicious column names

## Summary
Severity: High
Advisory: GHSA-r38f-c4h4-hqq2
CVE: CVE-2022-31197
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-r38f-c4h4-hqq2
Type: github-advisory

## Affected
- Maven: `org.postgresql:postgresql` — affected >=0 <42.2.26
- Maven: `org.postgresql:postgresql` — affected >=42.4.0 <42.4.1
- Maven: `org.postgresql:postgresql` — affected >=42.3.0 <42.3.7

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

The PGJDBC implementation of the `java.sql.ResultRow.refreshRow()` method is not performing escaping of column names so a malicious column name that contains a statement terminator, e.g. `;`, could lead to SQL injection. This could lead to executing additional SQL commands as the application's JDBC user.

User applications that do not invoke the `ResultSet.refreshRow()` method are not impacted.

User application that do invoke that method are impacted if the underlying database that they are querying via their JDBC application may be under the control of an attacker. The attack requires the attacker to trick the user into executing SQL against a table name who's column names would contain the malicious SQL and subsequently invoke the `refreshRow()` method on the ResultSet.

For example:

```sql
CREATE TABLE refresh_row_example (
  id     int PRIMARY KEY,
  "1 FROM refresh_row_example; SELECT pg_sleep(10); SELECT * " int
);
```

This example has a table with two columns. The name of the second column is crafted to contain a statement terminator followed by additional SQL. Invoking the `ResultSet.refreshRow()` on a ResultSet that queried this table, e.g. `SELECT * FROM refresh_row`, would cause the additional SQL commands such as the `SELECT pg_sleep(10)` invocation to be executed.

As the multi statement command would contain multiple results, it would not be possible for the attacker to get data directly out of this approach as the `ResultSet.refreshRow()` method would throw an exception. However, the attacker could execute any arbitrary SQL including inserting the data into another table that could then be read or any other DML / DDL statement.

Note that the application's JDBC user and the schema owner need not be the same. A JDBC application that executes as a privileged user querying database schemas owned by potentially malicious less-privileged users would be vulnerable. In that situation it may be possible for the malicious user to craft a schema that causes the application to execute commands as the privileged user.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Yes, versions 42.2.26, 42.3.7, and 42.4.1 have been released with a fix.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Check that you are not using the `ResultSet.refreshRow()` method.

If you are, ensure that the code that executes that method does not connect to a database that is controlled by an unauthenticated or malicious user. If your application only connects to its own database with a fixed schema with no DDL permissions, then you will not be affected by this vulnerability as it requires a maliciously crafted schema.

## References
- https://github.com/pgjdbc/pgjdbc/security/advisories/GHSA-r38f-c4h4-hqq2
- https://nvd.nist.gov/vuln/detail/CVE-2022-31197
- https://github.com/pgjdbc/pgjdbc/commit/739e599d52ad80f8dcd6efedc6157859b1a9d637
- https://github.com/pgjdbc/pgjdbc
- https://lists.debian.org/debian-lts-announce/2022/10/msg00009.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I6WHUADTZBBQLVHO4YG4XCWDGWBT4LRP
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UTFE6SV33P5YYU2GNTQZQKQRVR3GYE4S
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I6WHUADTZBBQLVHO4YG4XCWDGWBT4LRP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UTFE6SV33P5YYU2GNTQZQKQRVR3GYE4S
