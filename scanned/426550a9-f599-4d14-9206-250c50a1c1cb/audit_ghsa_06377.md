# [H] elFinder: ZIP extraction bypasses uploadDeny MIME filter allowing PHP file upload (RCE)

## Summary
Severity: High
Advisory: GHSA-gxmj-r5rf-ggwq
CVE: CVE-2026-81891
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-gxmj-r5rf-ggwq
Type: github-advisory

## Affected
- Packagist: `Studio-42/elFinder` — affected >=0 <2.1.70

## Details
### Summary

elFinder provides `uploadDeny` and `uploadAllow` options in its connector configuration to restrict which MIME types may be uploaded. When `uploadDeny` includes `text/x-php`, direct upload of `.php`, `.phtml`, and `.phar` files is correctly blocked. However, the `extract` command (ZIP decompression) internally calls `checkExtractItems()`, which invokes `mimetypeInternalDetect()` directly without passing the result through `mimeTypeNormalize()`. Because `phtml`, `phar`, and similar PHP-executable extensions are absent from `mime.types`, they are not resolved to `text/x-php` at the detection stage, causing the MIME filter to be silently bypassed. An attacker who is permitted to upload ZIP archives can therefore extract PHP-executable files into the web-accessible `files/` directory. If the server is configured to execute the affected extension (e.g., `.phtml`, `.phar`) as PHP — which is the case in common Apache and Nginx deployments — this results in Remote Code Execution.

---

### Details

elFinder's MIME validation pipeline for **direct uploads** (`upload` command) is:

```
mimetype()
  └─ mimetypeInternalDetect()   // stage 1: extension → MIME via mime.types
  └─ mimeTypeNormalize()        // stage 2: apply staticMimeMap
       phtml:* → text/x-php
       phar:*  → text/x-php
       php5:*  → text/x-php
  └─ allowPutMime()             // blocked: text/x-php ∈ uploadDeny
```

The `extract` command (`checkExtractItems()` in `elFinderVolumeDriver.class.php`, line 7110) uses a **shortened** pipeline:

```php
// line 7110 — stage 2 (mimeTypeNormalize) is never called
if ($chkMime
    && ($mimeByName = elFinderVolumeDriver::mimetypeInternalDetect($name))
    && !$this->allowPutMime($mimeByName)) {
```

Because `phtml` and `phar` are not present in `mime.types`, `mimetypeInternalDetect()` returns a generic type (e.g., `application/octet-stream`) for these extensions. Without `mimeTypeNormalize()`, the `staticMimeMap` entries that would map `phtml:*` → `text/x-php` are never applied, so `allowPutMime()` sees a non-blocked MIME and permits extraction.

**Affected extensions confirmed:** `.phtml`, `.phar`, `.php5`, `.php3`  
**Not bypassed:** `.php` (present in `mime.types`, detected as `text/x-php` in stage 1)

---

### PoC

**Requirements:**
- elFinder 2.1.69 deployed under Apache/Nginx (PHP-FPM or mod_php)
- Connector configured with `uploadDeny = ['text/x-php']` and `uploadAllow` including `application/zip`
- `files/` directory served under a public web path

**Step 1 — Confirm direct upload is blocked**
Open elFinder in a browser and click the **Upload** button.  
Select `hello.phtml` (content: `<?php phpinfo(); ?>`).  
→ Upload is rejected with: *"Upload file hello.phtml: File type not allowed (text/x-php)"*
<img width="1061" height="408" alt="1" src="https://github.com/user-attachments/assets/22f833d9-7d2a-4197-85c2-3b0eb19ecfbc" />


**Step 2 — Upload a ZIP containing the payload**
Create `bypass.zip` containing `hello.phtml`.  
Upload `bypass.zip` via the **Upload** button.  
→ ZIP is accepted (MIME: `application/zip` ∈ `uploadAllow`).
<img width="886" height="320" alt="2" src="https://github.com/user-attachments/assets/30c3498f-91f4-45cf-8c2b-cc806716e3a4" />


**Step 3 — Extract the ZIP**
Right-click `bypass.zip` in the file list → **Extract files**.  
→ `hello.phtml` appears in the file list without any error.  
→ File is now present at `{files_dir}/hello.phtml` on the server.
<img width="1123" height="792" alt="3" src="https://github.com/user-attachments/assets/49e7db8e-566c-4653-a57f-e80fb31ea61d" />


**Step 4 — Execute the extracted PHP file**

Navigate to:
```
http://<target>/elFinder/files/hello.phtml
```
→ Apache processes the file as PHP and renders the full `phpinfo()` output, confirming Remote Code Execution.

---
<img width="1059" height="739" alt="4" src="https://github.com/user-attachments/assets/ad85fdf7-bdc7-4514-bdec-e45cfb2e2bd3" />



### Impact

Any user with ZIP upload permission can bypass the `uploadDeny` MIME restriction, place PHP-executable files in a web-accessible directory, and achieve Remote Code Execution on the server.

**Concrete impact:**
- Arbitrary PHP code execution on the web server
- Full server environment disclosure via `phpinfo()` (paths, PHP version, loaded modules, environment variables)
- Potential access to server filesystem, database credentials, and internal network services
- Complete compromise of the web application if an attacker substitutes `phpinfo()` with a web shell (e.g., `<?php system($_GET['cmd']); ?>`)

**Extensions confirmed executable on Apache (default config):**
phtml, phar, php5, php3

**Recommended fix:**

Apply `mimeTypeNormalize()` inside `checkExtractItems()` so that the full MIME pipeline is used consistently:

```php
// elFinderVolumeDriver.class.php, line 7110
// Before (vulnerable):
$mimeByName = elFinderVolumeDriver::mimetypeInternalDetect($name)

// After (fixed):
$mimeByName = $this->mimeTypeNormalize(
    elFinderVolumeDriver::mimetypeInternalDetect($name),
    $name,
    pathinfo($name, PATHINFO_EXTENSION)
)
```

---

---

## References
- https://github.com/Studio-42/elFinder/security/advisories/GHSA-gxmj-r5rf-ggwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-81891
- https://github.com/Studio-42/elFinder/commit/191372c1bbebbd36fb55af79a84b9984861390ff
- https://github.com/Studio-42/elFinder/commit/dd73e702820c146a192969800ee674ecdb208365
- https://github.com/Studio-42/elFinder
- https://github.com/Studio-42/elFinder/releases/tag/2.1.70
