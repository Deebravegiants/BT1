# [M] RustDesk Client Accepts Unauthenticated stop-service Command via Strategy Payload

## Summary
Severity: Medium
Advisory: CVE-2026-30798
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-30798
Type: osv

## Details
Insufficient Verification of Data Authenticity, Improper Handling of Exceptional Conditions vulnerability in rustdesk-client RustDesk Client rustdesk-client on Windows, MacOS, Linux, iOS, Android (Heartbeat sync loop, strategy processing modules) allows Protocol Manipulation.

 This vulnerability is associated with program files src/hbbs_http/sync.Rs and program routines stop-service handler in heartbeat loop.



This issue affects RustDesk Client: through 1.4.8.

## References
- https://github.com/rustdesk/rustdesk,https://github.com/rustdesk/hbb_common
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30798.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30798
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk/releases
- https://rustdesk.com/docs/en/client/
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
