# [M] LibreNMS has a stored XSS in ExamplePlugin with Device's Notes

## Summary
Severity: Medium
Advisory: GHSA-c86q-rj37-8f85
CVE: CVE-2024-49758
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-c86q-rj37-8f85
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <24.10.0

## Details
### Summary

The application fail to sanitising inputs properly and rendering the code from user input to browser which allow an attacker to execute malicious javascript code.

### Details

User with Admin role can add Notes to a device, the application did not properly sanitize the user input, when the ExamplePlugin enable, if java script code is inside the device's Notes, its will be trigger.

### PoC

1. As an admin user, enable the ExamplePlugin.

![image](https://github.com/user-attachments/assets/409f3a0c-7fac-46e3-8140-84749a120dd9)

2. Add the payload `<img src="x" onerror="alert(document.cookie)">` into the device Notes

![image](https://github.com/user-attachments/assets/c2a57dbd-ea07-4166-8b29-61be6ad6c2b6)

3. Once visit the Overview of the Device, a pop-up will show up.

![image](https://github.com/user-attachments/assets/3c9b87c3-d010-49e7-bd13-4a715db4e0c3)

### Impact

It could allow authenticated users to execute arbitrary JavaScript code in the context of other users' sessions.
Impacted users could have their accounts compromised, enabling the attacker to perform unauthorized actions on their behalf.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-c86q-rj37-8f85
- https://nvd.nist.gov/vuln/detail/CVE-2024-49758
- https://github.com/librenms/librenms/commit/24b142d753898e273ec20b542a27dd6eb530c7d8
- https://github.com/librenms/librenms
