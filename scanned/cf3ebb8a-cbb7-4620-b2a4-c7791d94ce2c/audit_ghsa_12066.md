# [H] File Upload(RCE) Vulnerability in admidio

## Summary
Severity: High
Advisory: GHSA-95cq-p4w2-32w5
CVE: CVE-2026-32756
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-95cq-p4w2-32w5
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.7

## Details
### **Summary**

A critical unrestricted file upload vulnerability exists in the Documents & Files module of Admidio. Due to a design flaw in how CSRF token validation and file extension verification interact within `UploadHandlerFile.php`, an authenticated user with upload permissions can bypass file extension restrictions by intentionally submitting an invalid CSRF token. This allows the upload of arbitrary file types, including PHP scripts, which may lead to Remote Code Execution (RCE) on the server.

### **Details**

**1. Critical - Unrestricted File Upload leading to Remote Code Execution (RCE)**

**Root Cause Analysis:**

The root cause lies in a design flaw in `src/Infrastructure/Plugins/UploadHandlerFile.php`. The `UploadHandlerFile` class overrides two methods from its parent `UploadHandler` class:

- `handle_form_data($file, $index)` — Validates the CSRF token. On failure, it sets `$file->error` and returns. The request is **not** terminated.
- `handle_file_upload(...)` — Calls `parent::handle_file_upload()` to physically write the file to disk, then checks `if (!isset($file->error))` before running file extension validation (`allowedFileExtension()`).

The execution flow differs based on whether the CSRF token is valid:

- **Valid CSRF token**: `handle_form_data()` does not set an error → extension check runs → invalid extension causes the uploaded file to be deleted from disk.
- **Invalid CSRF token**: `handle_form_data()` sets `$file->error` → the `if (!isset($file->error))` guard in `handle_file_upload()` causes the extension validation to be skipped entirely → the cleanup code (`FileSystemUtils::deleteFileIfExists()`) is never reached → the file, already written to disk by the parent class, remains on the server and is directly accessible.

In summary, the file is always saved to disk by the parent class first. The extension check and cleanup only execute when no prior error exists. A deliberate CSRF token failure bypasses the extension filter while the file remains on disk.

**Affected code** (`src/Infrastructure/Plugins/UploadHandlerFile.php`):

```php
// File is physically saved to disk here, before any Admidio-specific checks
$file = parent::handle_file_upload($uploaded_file, $name, $size, $type, $error, $index, $content_range);

if (!isset($file->error)) {
    // Extension validation is only reached when no prior error is set.
    // If CSRF validation failed in handle_form_data(), this block is skipped
    // and the uploaded file is never cleaned up from disk.
    if (!$newFile->allowedFileExtension()) {
        throw new Exception('SYS_FILE_EXTENSION_INVALID');
    }
}
```

### **PoC**

Documents & Files Create folder
<img width="762" height="729" alt="image" src="https://github.com/user-attachments/assets/2c927482-851b-4945-93d6-6e7a1e3bc21f" />

<img width="749" height="690" alt="image" src="https://github.com/user-attachments/assets/72443c87-e15f-4312-9659-8cd0661a4dae" />


File Upload Try 1-1 (before request)
<img width="1856" height="635" alt="image" src="https://github.com/user-attachments/assets/d1ffaa12-aec1-45ff-a612-885d9554fb60" />


File Upload Try 1-2 (after request)
<img width="1850" height="855" alt="image" src="https://github.com/user-attachments/assets/4ece4aac-1255-4189-9048-45ff3df4abcf" />



File Upload Try 1-3 (After changing CSRF to a test value, request → PHP file upload succeeds)
<img width="1847" height="928" alt="image" src="https://github.com/user-attachments/assets/63f9d108-5e4f-4d32-96d2-09f9ad910873" />


✅ rcepoc.php Upload Success!
<img width="926" height="814" alt="image" src="https://github.com/user-attachments/assets/4de99c31-dc3c-44f2-9936-19c3da0dfffb" />


Access the rcepoc upload path confirmed in the response and check the web shell.
<img width="1635" height="922" alt="image" src="https://github.com/user-attachments/assets/0b770caf-e737-4cbd-97b9-ae191a8b79f5" />


🆗 WebShell Success
<img width="685" height="187" alt="image" src="https://github.com/user-attachments/assets/e90f162b-7949-41c4-9fd1-aad3b6365adf" />

<img width="794" height="209" alt="image" src="https://github.com/user-attachments/assets/f45dae74-a830-4761-af31-f2ac28eb2586" />


**Steps to Reproduce:**

1. Log in to Admidio as an authenticated user with upload permissions on the Documents & Files module.
2. Navigate to a folder in the Documents & Files module and open the file upload dialog.
3. Intercept the upload POST request to `/system/file_upload.php?module=documents_files&mode=upload_files&uuid=<folder_uuid>` using a proxy tool such as Burp Suite.
4. Replace the value of the `adm_csrf_token` field with an arbitrary invalid string (e.g., `webshellgogo`).
5. Set the file to be uploaded to a PHP webshell (e.g., `<?php system($_GET[1]); ?>`).
6. Forward the modified request.
7. Observe that the server responds with HTTP `200 OK`. The JSON body contains `"error":"Invalid or missing CSRF token!"`, yet the file is physically present on the server at the path indicated in the `url` field.
8. Access the uploaded PHP file directly via the URL provided in the response — arbitrary command execution is confirmed.

### **Impact**

- An authenticated attacker with upload permissions can bypass file extension validation and upload arbitrary server-side scripts such as PHP webshells.
- This leads to Remote Code Execution (RCE), potentially resulting in full server compromise, sensitive data exfiltration, and lateral movement.
- While authentication is required, the attack is not limited to administrators — any member granted upload rights may exploit this vulnerability, making the attack surface broader than it may initially appear.

### **Remediation Measures**

- The extension validation logic should be executed independently of the CSRF error state. It is recommended to move the extension check and the corresponding cleanup outside of the `if (!isset($file->error))` block so that files with disallowed extensions are always removed from disk, regardless of other errors.
- Rather than relying on a blacklist of dangerous extensions (e.g., `.php`, `.phar`, `.phtml`), it is strongly recommended to implement a **whitelist** of permitted extensions appropriate to a documents module (e.g., `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.txt`).
- CSRF token validation should either be performed before the file is written to disk, or a validation failure should result in immediate request termination rather than merely setting an error flag on the file object.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-95cq-p4w2-32w5
- https://nvd.nist.gov/vuln/detail/CVE-2026-32756
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.7
