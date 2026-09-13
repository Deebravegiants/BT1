# [M] CVE-2025-6024

## Summary
Severity: Medium
Advisory: CVE-2025-6024
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2025-6024
Type: osv

## Details
The authentication endpoint fails to encode user-supplied input before rendering it in the web page, allowing for script injection.
An attacker can leverage this by injecting malicious scripts into the authentication endpoint. This can result in the user's browser being redirected to a malicious website, manipulation of the web page's user interface, or the retrieval of information from the browser. However, session hijacking is not possible due to the httpOnly flag protecting session-related cookies.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2026/WSO2-2025-4251/
