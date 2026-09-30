# [M] RustDesk Server Generates Config Strings Using Reversible Encoding (Base64 + Reverse) Instead of Encryption

## Summary
Severity: Medium
Advisory: CVE-2026-3598
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-3598
Type: osv

## Details
Use of a Broken or Risky Cryptographic Algorithm vulnerability in rustdesk-server-pro RustDesk Server Pro rustdesk-server-pro on Windows, MacOS, Linux (Config string generation, web console export modules) allows Retrieve Embedded Sensitive Data. This vulnerability is associated with program routines Config export/generation routines.

This issue affects RustDesk Server Pro: through 1.7.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3598.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3598
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk-server-pro/releases
- https://rustdesk.com/docs/en/client/
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
