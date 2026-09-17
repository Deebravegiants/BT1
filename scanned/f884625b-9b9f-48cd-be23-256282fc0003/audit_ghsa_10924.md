# [H] Admidio allows Unauthenticated Access to Role-Restricted documents via neutralized .htaccess

## Summary
Severity: High
Advisory: GHSA-7fh7-8xqm-3g88
CVE: CVE-2026-34381
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-7fh7-8xqm-3g88
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=5.0.0 <5.0.8

## Details
### Summary

Admidio relies on `adm_my_files/.htaccess` to deny direct HTTP access to uploaded documents. The Docker image ships with `AllowOverride None` in the Apache configuration, which causes Apache to silently ignore all `.htaccess` files. As a result, any file uploaded to the
documents module regardless of the _role-based_ permissions configured in the UI, is directly accessible over HTTP without authentication by anyone who knows the file path. The file path is disclosed in the upload response JSON.

---

### Root Cause

**File 1: Intended protection (ignored):**  
`adm_my_files/.htaccess`
```apache
Require all denied
```
<img width="408" height="403" alt="imagen" src="https://github.com/user-attachments/assets/95f0d389-a1a9-4dc4-9840-7f189d2c58ff" />

**File 2: Apache config that neutralizes it:**  

* Command in order to search in Docker container: `docker exec admidio-sec-app cat /etc/apache2/apache2.conf`

`/etc/apache2/apache2.conf` (Docker image)
```apache
<Directory ${APACHE_DOCUMENT_ROOT}>
    AllowOverride None
</Directory>
```

<img width="492" height="328" alt="imagen" src="https://github.com/user-attachments/assets/2f2e09b1-0c2e-4932-8698-a40f6b92e917" />


`AllowOverride None` instructs Apache to skip `.htaccess` processing entirely, the deny rule never executes. The upload directory is inside the web root at `/opt/app-root/src/adm_my_files/` and returns **HTTP 200** for direct requests.

**File 3: Upload response leaks the direct URL:**  `system/file_upload.php`, upload response JSON:

<img width="1528" height="624" alt="imagen" src="https://github.com/user-attachments/assets/50e66fde-ff41-4efa-adc9-ceeb5b23a97d" />

```json
{
  "files": [{
    "name": "sensitive_poc.txt",
    "url": "http://TARGET/adm_my_files/documents_research/TEST-SENSITIVE/sensitive_poc.txt"
  }]
}
```

### Verified PoC

**Step 1: Admin creates a restricted folder (visible only to Administrator role):**  
> `modules/documents-files.php` → permissions set to role `Administrator` only.

<img width="1161" height="784" alt="imagen" src="https://github.com/user-attachments/assets/25d81e44-9a7c-4991-b72e-6e664d176695" />

**Step 2: Admin uploads a file to the restricted folder.**  
> Upload response returns:
```
http://TARGET/adm_my_files/documents_research/TEST-SENSITIVE/sensitive_poc.txt
```

<img width="1239" height="294" alt="imagen" src="https://github.com/user-attachments/assets/84c1bcd1-47d7-4115-ac0f-653b0a6d7301" />

**Step 3: Unauthenticated request retrieves the file:**
```bash
curl -X GET 'http://TARGET/adm_my_files/documents_research/TEST-SENSITIVE/sensitive_poc.txt'
# Response: full file contents — no authentication required
```

<img width="1051" height="150" alt="imagen" src="https://github.com/user-attachments/assets/1ed7fab7-59cb-4d5b-8c60-12108490d1e4" />

**Step 4: Confirm folder is role-restricted:**
```sql
SELECT fil_name, fol_name, fol_public FROM adm_files JOIN adm_folders ON fil_fol_id = fol_id 
ORDER BY fil_id DESC LIMIT 5; -- fol_public = 0, role restricted — yet file is publicly accessible
```
---

### Impact

- Any document uploaded to **Admidio** including files restricted to specific roles is publicly accessible via direct HTTP request with no authentication required
- **Role-based** access control on the documents module is completely bypassed at the filesystem level
- Sensitive organizational documents (contracts, member data, financial records) are exposed to anyone who can guess or construct the file path
- The upload API response discloses the direct URL to the uploader, making path enumeration trivial

### Recommended Fix

**Option 1 (preferred): Enable AllowOverride in Apache config:**
```apache
<Directory /opt/app-root/src/adm_my_files>
    AllowOverride All
</Directory>
```

**Option 2: Move uploads outside the web root:**  
Store uploaded files in a directory outside `DOCUMENT_ROOT` and serve them exclusively through Admidio's download handler (`modules/documents-files.php?mode=download`), which enforces role checks before serving the file.

**Option 3: Apache-level explicit deny (does not require .htaccess):**
```apache
<Directory /opt/app-root/src/adm_my_files>
    Require all denied
</Directory>
```
> The most robust long-term fix is Option 2 — moving uploads outside the web root eliminates the dependency on Apache configuration correctness entirely.

**Reported by:** Juan Felipe Oz [@JF0x0r](https://x.com/PwnedRar_)
> [LinkedIn](https://www.linkedin.com/in/juanfelipeoz/)

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-7fh7-8xqm-3g88
- https://nvd.nist.gov/vuln/detail/CVE-2026-34381
- https://github.com/Admidio/admidio/commit/5f770c1ca81a4f6b02136280cd63316a35aabaaf
- https://github.com/Admidio/admidio
