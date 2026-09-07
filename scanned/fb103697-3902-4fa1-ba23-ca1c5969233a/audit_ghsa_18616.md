# [M] LibreNMS has a Stored XSS vulnerability in its Alert Transport name field

## Summary
Severity: Medium
Advisory: GHSA-frc6-pwgr-c28w
CVE: CVE-2025-62411
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-frc6-pwgr-c28w
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <25.10.0

## Details
### Summary

LibreNMS <= 25.8.0 contains a **Stored Cross-Site Scripting (XSS)** vulnerability in the Alert Transports management functionality. When an administrator creates a new Alert Transport, the value of the `Transport name` field is stored and later rendered in the **Transports** column of the **Alert Rules** page without proper input validation or output encoding. This leads to arbitrary JavaScript execution in the admin’s browser.

### Details

* **Injection point:** `Transport name` field in `/alert-transports`.
* **Execution point:** **Transports** column in `/alert-rules`.
* **Scope:** Only administrators can create Alert Transports, and only administrators can view the affected Alert Rules page. Therefore, both exploitation and impact are limited to admin users.

### Steps to reproduce

1. Log in with an administrator account.
2. Navigate to:

   ```
   http://localhost:8000/alert-transports
   ```
3. Click **Create alert transport** and provide the following values:

   * **Transport name:**

     ```html
     'onfocus='alert(1)' autofocus=
     ```
   * **Default Alert:** `ON`
   * **Email:** `test@gmail.com` (or any valid email)
   
    Save the transport.
   
4. Navigate to ```http://localhost:8000/alert-rules```. A popup `alert(1)` is triggered, confirming that the payload executes.
<img width="1829" height="396" alt="image" src="https://github.com/user-attachments/assets/932ba17d-214d-4253-80b8-62539d1cfa28" />

### Impact

Only accounts with the admin role who access the **Alert Rules** page (`http://localhost:8000/alert-rules`) are affected.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-frc6-pwgr-c28w
- https://nvd.nist.gov/vuln/detail/CVE-2025-62411
- https://github.com/librenms/librenms/commit/706a77085f4d5964f7de9444208ef707e1f79450
- https://github.com/librenms/librenms/commit/e1ead366239b57e88f9a06d4f7c213b1e2530cd8
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/25.10.0
