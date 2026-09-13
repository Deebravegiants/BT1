# [H] @budibase/server: Command Injection in PostgreSQL Dump Command

## Summary
Severity: High
Advisory: GHSA-726g-59wr-cj4c
CVE: CVE-2026-25041
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-726g-59wr-cj4c
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.23.32

## Details
**Location**: `packages/server/src/integrations/postgres.ts:529-531`  

#### Description
The PostgreSQL integration constructs shell commands using user-controlled configuration values (database name, host, password, etc.) without proper sanitization. The password and other connection parameters are directly interpolated into a shell command.

#### Code Reference
```529:531:packages/server/src/integrations/postgres.ts
    const dumpCommand = `PGPASSWORD="${
      this.config.password
    }" pg_dump --schema-only "${dumpCommandParts.join(" ")}"`
```

#### Attack Vector
An attacker who can control database configuration values (e.g., through compromised credentials or configuration injection) can inject shell commands. For example:
- Password: `password"; malicious-command; echo "`
- Database name: `db"; rm -rf /; echo "`

#### Impact
- Remote code execution
- System compromise
- Data exfiltration

#### Recommendation
1. Use environment variables for sensitive values instead of command-line arguments
2. Validate and sanitize all configuration values
3. Use proper escaping for shell arguments
4. Consider using a PostgreSQL library's native dump functionality instead of shell commands

#### Example Fix
```typescript
import { execFile } from "child_process"
import { promisify } from "util"
const execFileAsync = promisify(execFile)

// Use execFile with proper argument handling
const env = {
  ...process.env,
  PGPASSWORD: this.config.password
}

const args = [
  "--schema-only",
  "--host", this.config.host,
  "--port", this.config.port.toString(),
  "--username", this.config.user,
  "--dbname", this.config.database
]

try {
  const { stdout } = await execFileAsync("pg_dump", args, { env })
  return stdout
} catch (error) {
  // Handle error
}
```

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-726g-59wr-cj4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-25041
- https://github.com/Budibase/budibase/commit/9fdbff32fb9e69650ba899a799e13f80d9b09e93
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/blob/f34d545602a7c94427bae63312a5ee9bf2aa6c85/packages/server/src/integrations/postgres.ts#L529-L531
