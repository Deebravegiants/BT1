# [C] Horrila Stored XSS Vulnerability via Ticket Comment section

## Summary
Severity: Critical
Advisory: CVE-2025-59832
Aliases: GHSA-8x78-6q9g-hv2h
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2025-09-25
Source: https://osv.dev/vulnerability/CVE-2025-59832
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). Prior to version 1.4.0, there is a stored XSS vulnerability in the ticket comment editor. A low-privilege authenticated user could run arbitrary JavaScript in an admin’s browser, exfiltrate the admin’s cookies/CSRF token, and hijack their session. This issue has been patched in version 1.4.0.

## References
- https://github.com/Mmo-kali/CVE/blob/main/CVE-2025-59832/2025-08-Horilla_Vulnerability_1.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59832.json
- https://github.com/horilla-opensource/horilla/security/advisories/GHSA-8x78-6q9g-hv2h
- https://nvd.nist.gov/vuln/detail/CVE-2025-59832
