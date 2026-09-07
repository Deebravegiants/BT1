# [H] Maho is Vulnerable to Authenticated Remote Code Execution via File Upload

## Summary
Severity: High
Advisory: GHSA-vgmm-27fc-vmgp
CVE: CVE-2025-58449
CWE: CWE-646
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-vgmm-27fc-vmgp
Type: github-advisory

## Affected
- Packagist: `mahocommerce/maho` — affected >=0 <25.9.0

## Details
### Summary
In Maho 25.7.0, an authenticated staff user with access to the `Dashboard` and `Catalog\Manage Products` permissions can create a custom option on a listing with a file input field. By allowing file uploads with a `.php` extension, the user can use the filed to upload malicious PHP files, gaining remote code execution

### Details
An  user with the `Dashboard` and `Catalog\Manage Products` permissions can abuse the product custom options feature to bypass the application’s file upload restrictions.

When creating a product custom option of type file upload, the user is allowed to define their own extension whitelist. This bypasses the application’s normal enforced whitelist and permits disallowed extensions, including `.php`.

The file uploaded by the custom option is then written to a predictable location:
```
/public/media/custom_options/<first char of filename>/<second char of filename>/<md5 of file contents>.php
```
Because this path is directly accessible under the application’s webroot, an attacker can then request the uploaded file via HTTP, causing the server to execute the PHP payload.

### PoC
1. Sign in to the `/admin` dashboard as a staff user. Ensure the user's role has access to the `Dashboard` and `Catalog\Manage Products` permissions.
2. Navigate to a product catalog listing, for example by clicking on a product linked within the `Most Viewed Products` tab on the dashboard.
<img width="648" height="194" alt="image" src="https://github.com/user-attachments/assets/1ab69182-68ea-48e4-b50b-46ccf70f40bb" />

3. Navigate to the "Custom Options" tab on the product, and create a custom option with a file upload field. Add `.php` as an allowed extension to the file upload configuration. Save the configuration after making the changes.
<img width="836" height="391" alt="image" src="https://github.com/user-attachments/assets/5abe7d80-c16d-4b54-9a19-799bda1bcc34" />

4. In a private window, navigate to the customer facing page for the product, and upload a reverse shell PHP file through the newly configured option. Then click "Add to cart" to complete the upload.
<img width="473" height="286" alt="image" src="https://github.com/user-attachments/assets/326ce37e-026a-4211-8e95-6f5f310727df" />

5. Calculate the location of the uploaded file on the web server as 
```
/public/media/custom_options/<first char of filename>/<second char of filename>/<md5 of file contents>.php
```
6. Navigate to the above path directly to execute the file contents and trigger the reverse shell.
<img width="910" height="339" alt="image" src="https://github.com/user-attachments/assets/e0e52607-81d5-4dc2-8550-ef324182f889" />

### Impact
This vulnerability allows remote code execution (RCE) on the server. It requires only the Catalog\Manage Products permission, and does not need full administrative access. By leveraging the custom option upload feature, an attacker can bypass the application’s normal file upload protections and execute arbitrary PHP code within the webroot.

### Suggested Remediation
Enforce a whitelist of allowed extensions a user is allowed to configure for file upload fields in Custom Options.

## References
- https://github.com/MahoCommerce/maho/security/advisories/GHSA-vgmm-27fc-vmgp
- https://nvd.nist.gov/vuln/detail/CVE-2025-58449
- https://github.com/MahoCommerce/maho/commit/db54a1b44e9b3fd26b27ca4d5ece0af99c4dcb53
- https://github.com/MahoCommerce/maho
