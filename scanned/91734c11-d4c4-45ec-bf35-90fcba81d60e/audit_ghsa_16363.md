# [C] org.postgresql:postgresql vulnerable to SQL Injection via line comment generation

## Summary
Severity: Critical
Advisory: GHSA-24rp-q3w6-vc56
CVE: CVE-2024-1597
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-24rp-q3w6-vc56
Type: github-advisory

## Affected
- Maven: `org.postgresql:postgresql` — affected >=0 <42.2.28
- Maven: `org.postgresql:postgresql` — affected >=42.3.0 <42.3.9
- Maven: `org.postgresql:postgresql` — affected >=42.4.0 <42.4.4
- Maven: `org.postgresql:postgresql` — affected >=42.5.0 <42.5.5
- Maven: `org.postgresql:postgresql` — affected >=42.6.0 <42.6.1
- Maven: `org.postgresql:postgresql` — affected >=42.7.0 <42.7.2

## Details
# Impact
SQL injection is possible when using the non-default connection property `preferQueryMode=simple` in combination with application code that has a vulnerable SQL that negates a parameter value.

There is no vulnerability in the driver when using the default query mode. Users that do not override the query mode are not impacted.

# Exploitation

To exploit this behavior the following conditions must be met:

1. A placeholder for a numeric value must be immediately preceded by a minus (i.e. `-`)
1. There must be a second placeholder for a string value after the first placeholder on the same line. 
1. Both parameters must be user controlled.

The prior behavior of the driver when operating in simple query mode would inline the negative value of the first parameter and cause the resulting line to be treated as a `--` SQL comment. That would extend to the beginning of the next parameter and cause the quoting of that parameter to be consumed by the comment line. If that string parameter includes a newline, the resulting text would appear unescaped in the resulting SQL.

When operating in the default extended query mode this would not be an issue as the parameter values are sent separately to the server. Only in simple query mode the parameter values are inlined into the executed SQL causing this issue.

# Example

```java
PreparedStatement stmt = conn.prepareStatement("SELECT -?, ?");
stmt.setInt(1, -1);
stmt.setString(2, "\nWHERE false --");
ResultSet rs = stmt.executeQuery();
```

The resulting SQL when operating in simple query mode would be:

```sql
SELECT --1,'
WHERE false --'
```

The contents of the second parameter get injected into the command. Note how both the number of result columns and the WHERE clause of the command have changed. A more elaborate example could execute arbitrary other SQL commands.

# Patch
Problem will be patched upgrade to 42.7.2, 42.6.1, 42.5.5, 42.4.4, 42.3.9, 42.2.28, 42.2.28.jre7

The patch fixes the inlining of parameters by forcing them all to be serialized as wrapped literals. The SQL in the prior example would be transformed into:

```sql
SELECT -('-1'::int4), ('
WHERE false --')
```

# Workarounds
Do not use the connection property`preferQueryMode=simple`. (*NOTE: If you do not explicitly specify a query mode then you are using the default of `extended` and are not impacted by this issue.*)

## References
- https://github.com/pgjdbc/pgjdbc/security/advisories/GHSA-24rp-q3w6-vc56
- https://nvd.nist.gov/vuln/detail/CVE-2024-1597
- https://github.com/pgjdbc/pgjdbc/commit/06abfb78a627277a580d4df825f210e96a4e14ee
- https://github.com/pgjdbc/pgjdbc/commit/93b0fcb2711d9c1e3a2a03134369738a02a58b40
- https://github.com/pgjdbc/pgjdbc
