# [H] RustDesk HTTP Client Silently Accepts Invalid TLS Certificates After Handshake Failure

## Summary
Severity: High
Advisory: CVE-2026-30794
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-30794
Type: osv

## Details
Improper Certificate Validation vulnerability in rustdesk-client RustDesk Client rustdesk-client on Windows, MacOS, Linux, iOS, Android (HTTP API client, TLS transport modules) allows Adversary in the Middle (AiTM). This vulnerability is associated with program files src/hbbs_http/http_client.Rs and program routines TLS retry with danger_accept_invalid_certs(true).

This issue affects RustDesk Client: through 1.4.5.

## References
- https://github.com/rustdesk/rustdesk,https://github.com/rustdesk/hbb_common
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30794.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30794
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk
- https://github.com/rustdesk/rustdesk/releases
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
