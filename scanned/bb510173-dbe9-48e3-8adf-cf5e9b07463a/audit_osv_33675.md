# [M] FreeScout Vulnerable to Arbitrary File Upload

## Summary
Severity: Medium
Advisory: CVE-2025-48471
Aliases: GHSA-h2f3-932h-v38j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/CVE-2025-48471
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.179, the application does not check or performs insufficient checking of files uploaded to the application. This allows files to be uploaded with the phtml and phar extensions, which can lead to remote code execution if the Apache web server is used. This issue has been patched in version 1.8.179.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48471.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-h2f3-932h-v38j
- https://nvd.nist.gov/vuln/detail/CVE-2025-48471
- https://github.com/freescout-help-desk/freescout/commit/e136660e8dbc220454b8d3f646dd1b144e49e9ed
