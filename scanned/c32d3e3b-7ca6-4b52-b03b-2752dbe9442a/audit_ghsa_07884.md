# [C] Rust has Critical Stored XSS in Preview Modal, leading to Administrative Account Takeover

## Summary
Severity: Critical
Advisory: GHSA-v9fg-3cr2-277j
CVE: CVE-2026-27822
CWE: CWE-79
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-v9fg-3cr2-277j
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=0 <1.0.0-alpha.83

## Details
### Summary
A Stored Cross-Site Scripting (XSS) vulnerability in the RustFS Console allows an attacker to execute arbitrary JavaScript in the context of the management console. By bypassing the PDF preview logic, an attacker can steal administrator credentials from `localStorage`, leading to full account takeover and system compromise.

### Details
The vulnerability exists due to improper validation of the response content type during the file preview process and a lack of origin separation between the S3 object delivery and the management console.

1. **Origin of Credentials**: The RustFS Console stores highly sensitive S3 credentials (AccessKey, SecretKey, SessionToken) in the browser's `localStorage`.
   - **File**: `console/composables/useAuth.ts`
   - **Evidence**: [Lines 14](https://github.com/rustfs/console/blob/c2bd75adacad0d0182c32d5271e8ff150c4a02db/composables/useAuth.ts#L14) and [18-25](https://github.com/rustfs/console/blob/c2bd75adacad0d0182c32d5271e8ff150c4a02db/composables/useAuth.ts#L18-L25) show that credentials are held in `useLocalStorage('auth.credentials', {})` and `useLocalStorage('auth.permanent', undefined)`.
2. **Insecure Preview Implementation**: In `console/components/object/preview-modal.vue`, the application identifies a PDF file based on its extension or metadata and [renders it using an `<iframe>`](https://github.com/rustfs/console/blob/6ab024be1c49bc9549a24ed1d09348f5e7039876/components/object/preview-modal.vue#L10).
3. **Same-Origin Vulnerability**: RustFS typically hosts the management console and the S3 API on the same origin (e.g., the same IP and port). 
4. **Bypass Attack**: An attacker can upload a file named `xss.pdf` but set its `Content-Type` metadata to `text/html`. Because the `iframe` is hosted on the same origin as the console, the executed script has unrestricted access to the parent window's `localStorage`.

### PoC
<img width="6006" height="3096" alt="CleanShot 2026-02-01 at 18 36 54@2x" src="https://github.com/user-attachments/assets/f2f5dae6-1e19-4133-9a69-f7d8ec604dad" />

This PoC demonstrates how to steal a victim's administrative credentials by tricking them into previewing a malicious file.

**1. Create the malicious payload (`xss.html`):**
```html
<script>
  alert('XSS Success!\nLocalStorage Data: ' + JSON.stringify(window.parent.localStorage));
</script>
```

**2. Setup the environment and upload the payload:**
```bash
# 1. Create a target bucket
mc mb rustfs/my-bucket

# 2. Upload the HTML file as a PDF with HTML content type
mc cp xss.html rustfs/my-bucket/xss.pdf --attr "Content-Type=text/html"
```

**3. Trigger the vulnerability:**
1. Login to the RustFS Console as an administrator.
2. Navigate to `my-bucket`.
3. Click the "Preview" button for the `xss.pdf` file.
4. The JavaScript executes, demonstrating access to the administrative session data.

### Impact
- **Character**: Stored Cross-Site Scripting (XSS).
- **Target**: System Administrators using the Console.
- **Result**: Full Account Takeover (ATO). An attacker gains the victim's `AccessKeyId`, `SecretAccessKey`, and `SessionToken`. This allows the attacker to perform any administrative action, including deleting data, creating backdoors, or downloading the entire filesystem via the S3 API.

### Proposed Mitigation
1. **Origin Separation**: Implement a dedicated domain for data delivery (e.g., `*.data.rustfs.io`) that is different from the console domain. This leverages the Same-Origin Policy (SOP) to isolate user-uploaded content.
2. **Security Headers**: Implement strict security headers in the backend:
   - `Content-Security-Policy (CSP)`: Disallow inline scripts and restrict script execution.
   - `X-Content-Type-Options: nosniff`: Prevent browsers from sniffing and executing content that differs from the declared type.

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-v9fg-3cr2-277j
- https://nvd.nist.gov/vuln/detail/CVE-2026-27822
- https://github.com/rustfs/rustfs
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-alpha.83
