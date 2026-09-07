# [M] LibreNMS allows stored XSS in Alert Template name field

## Summary
Severity: Medium
Advisory: GHSA-vxq6-8cwm-wj99
CVE: CVE-2025-55296
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-18
Source: https://github.com/advisories/GHSA-vxq6-8cwm-wj99
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <25.8.0

## Details
### Summary

A stored Cross-Site Scripting (XSS) vulnerability exists in LibreNMS (<= 25.6.0) in the Alert Template creation feature. This allows a user with the **admin role** to inject malicious JavaScript, which will be executed when the template is rendered, potentially compromising other admin accounts.

---
### Details

In the LibreNMS web UI, when a user with the **admin role** visits `/templates` and clicks **"Create new alert template"**, the **"Template name"** field fails to properly sanitize input. By inserting a payload like:

```
&lt;script>alert(document.cookie)&lt;/script> 
```

and filling the other fields with arbitrary content (e.g., `test`), once the template is saved, the script is executed. This confirms that user input is stored and later rendered without proper output encoding.

This vulnerability can be exploited for session hijacking, data theft, or other malicious actions targeting other admin users.

---
### PoC

1. Log in to LibreNMS using an account with the **admin role**.
2. Navigate to: `http://localhost:8000/templates`.
3. Click the **"Create new alert template"** button.
4. Input the following into the **Template name** field:

   ```
   &lt;script>alert(document.cookie)&lt;/script>
   ```
5. Fill the remaining fields (`Template`, `Alert title`, `Recovery title`) with arbitrary content such as `test`.
6. Click **"Create template"**.
7. Upon saving, a JavaScript alert pops up, confirming the stored XSS is triggered.
<img width="1574" height="848" alt="image" src="https://github.com/user-attachments/assets/bc482874-c47e-48e3-83b6-cb4a9dcf4a53" />

---
### Impact

 **Type**: Stored Cross-Site Scripting (XSS)
 **Affected users**: Only accounts with the **admin role** who access the Alert Templates page (`http://localhost:8000/templates`) are affected.
 **Attackers need**: Authenticated admin-level access.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-vxq6-8cwm-wj99
- https://nvd.nist.gov/vuln/detail/CVE-2025-55296
- https://github.com/librenms/librenms/commit/8ade3d827d317f5ac4b336617aafff865f825958
- https://github.com/librenms/librenms
