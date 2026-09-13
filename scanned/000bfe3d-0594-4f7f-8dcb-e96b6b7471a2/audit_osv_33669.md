# [M] Schule Has Client-Side Role-Based Access Control (RBAC) Bypass Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-48373
Aliases: GHSA-37h9-qq7c-6mc9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2025-48373
Type: osv

## Details
Schule is open-source school management system software. The application relies on client-side JavaScript (index.js) to redirect users to different panels based on their role. Prior to version 1.0.1, this implementation poses a serious security risk because it assumes that the value of data.role is trustworthy on the client side. Attackers can manipulate JavaScript in the browser (e.g., via browser dev tools or intercepting API responses) and set data.role to any arbitrary value (e.g., "admin"), gaining unauthorized access to restricted areas of the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48373.json
- https://github.com/schule111/Schule/security/advisories/GHSA-37h9-qq7c-6mc9
- https://nvd.nist.gov/vuln/detail/CVE-2025-48373
- https://github.com/schule111/Schule/commit/cbf7f509c37acd69b4ab8ee19d842de867b46b7e
