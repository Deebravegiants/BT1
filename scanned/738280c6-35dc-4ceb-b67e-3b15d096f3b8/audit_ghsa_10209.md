# [H] appsmith has SQL Injection in FilterDataService via Unsafe DROP TABLE Execution

## Summary
Severity: High
Advisory: GHSA-h8cj-hpmg-636v
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-h8cj-hpmg-636v
Type: github-advisory

## Affected
- Maven: `com.appsmith:interfaces` — affected >=0 <1.99

## Details
### Summary
A SQL injection vulnerability exists in `FilterDataServiceCE.java` where the `dropTable` method constructs a SQL `DROP TABLE` statement using string concatenation with the table name. If the table name is derived from user input, this allows for arbitrary SQL command execution.

### Details
The vulnerability is located in `app/server/appsmith-interfaces/src/main/java/com/appsmith/external/services/ce/FilterDataServiceCE.java`.

Line 627 in `dropTable` method:
```java
public void dropTable(String tableName) {
    String dropTableQuery = "DROP TABLE " + tableName + ";";
    executeDbQuery(dropTableQuery);
}
```

The `tableName` argument is concatenated directly into the SQL string without validation or escaping.

### PoC
If `dropTable` is exposed to user input (e.g., via a utility API that accepts a table name to clean up), an attacker could provide a value like:
`valid_table; DROP TABLE users; --`

The resulting query would be:
`DROP TABLE valid_table; DROP TABLE users; --;`

This would delete the intended table and then delete the `users` table (or execute any other injected SQL).

### Impact
*   **Type:** SQL Injection
*   **Impact:** Data Loss (Drop Table), potentially Data Exfiltration or Modification depending on database permissions.
*   **Who is impacted:** Appsmith server instances.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-h8cj-hpmg-636v
- https://github.com/appsmithorg/appsmith/commit/c8023ba4b3b54204ff3309c9e5c33664ad15ba32
- https://github.com/appsmithorg/appsmith
