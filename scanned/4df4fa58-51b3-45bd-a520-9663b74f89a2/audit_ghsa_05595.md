# [H] Redaxo has Path Traversal in Backup Addon Leading to Arbitrary File Read

## Summary
Severity: High
Advisory: GHSA-824x-88xg-cwrv
CVE: CVE-2026-21857
CWE: CWE-22, CWE-24
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-824x-88xg-cwrv
Type: github-advisory

## Affected
- Packagist: `redaxo/source` — affected >=0 <5.20.2

## Details
### Summary
Authenticated users with backup permissions can read arbitrary files within the webroot via path traversal in the Backup addon's file export functionality.
<img width="664" height="899" alt="image" src="https://github.com/user-attachments/assets/fd1ca69e-b275-4daf-9a62-621cde6525f5" />
<img width="2358" height="445" alt="image" src="https://github.com/user-attachments/assets/fad81152-9e1b-413e-9823-09540a23e2fb" />


### Details
The Backup addon does not validate the `EXPDIR` POST parameter against the UI-generated allowlist of permitted directories.  
An attacker can supply relative paths containing `../` sequences (or even absolute paths inside the document root) to include any readable file in the generated `.tar.gz` archive.

Vulnerable code:
- `redaxo/src/addons/backup/pages/export.php` (lines 72-76) – directly uses `$_POST['EXPDIR']`
- `redaxo/src/addons/backup/lib/backup.php` (lines ~413 & ~427) – concatenates unsanitized user input with base path

This allows disclosure of sensitive files such as:
- `redaxo/data/core/config.yml` → database credentials + password hashes of all backend users
- `.env`, custom configuration files, logs, uploaded malicious files, etc.

### Affected versions
≤ 5.20.1 (confirmed working)

### Patched versions
None (as of 2025-12-09)

### PoC – Extracting database credentials and password hashes
1. Log in as any user with Backup permission
2. Go to Backup → Export → Files

<img width="1240" height="960" alt="image" src="https://github.com/user-attachments/assets/bc05ba18-9664-4be2-b637-4fec3a0f409a" />

3. Intercept the request with Burp Suite 

<img width="2184" height="478" alt="image" src="https://github.com/user-attachments/assets/9fa754a1-2cd0-4d3d-a5cc-cfa34c8a1718" />

4. Change one `EXPDIR[]` value to `../../../../var/www/html/redaxo/data/core`

<img width="978" height="591" alt="image" src="https://github.com/user-attachments/assets/d15f5c7f-b72c-44cc-9be2-da8d3f26f124" />

5. Send request → download archive
<img width="423" height="131" alt="image" src="https://github.com/user-attachments/assets/db8a8bda-cdaf-4dea-812f-1e312da908e2" />

6. Extract and open `data/core/config.yml`
<img width="859" height="281" alt="image" src="https://github.com/user-attachments/assets/c8112ce1-5a1d-435f-953b-7eb4e711e042" />

Result: plaintext database password 
<img width="2534" height="1198" alt="image" src="https://github.com/user-attachments/assets/218ae917-868a-437e-98b0-6471b82c0b10" />

### Impact
Full compromise of the REDAXO installation:
- Database takeover
- Password hash extraction → offline cracking → admin access
- When combined with other vulnerabilities → RCE

CVSS 4.0 vector & score below.

### Credits
Discovered by: Łukasz Rybak

## References
- https://github.com/redaxo/redaxo/security/advisories/GHSA-824x-88xg-cwrv
- https://nvd.nist.gov/vuln/detail/CVE-2026-21857
- https://github.com/redaxo/redaxo
- https://github.com/redaxo/redaxo/releases/tag/5.20.2
