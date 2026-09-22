# [M] RustDesk Client Blindly Merges Unauthenticated Strategy Payloads, Bypassing Local Security Settings

## Summary
Severity: Medium
Advisory: CVE-2026-30792
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-30792
Type: osv

## Details
A vulnerability in rustdesk-client RustDesk Client rustdesk-client on Windows, MacOS, Linux, iOS, Android, WebClient (Strategy sync, HTTP API client, config options engine modules) allows Application API Message Manipulation via Man-in-the-Middle.

 This vulnerability is associated with program files src/hbbs_http/sync.Rs, hbb_common/src/config.Rs and program routines Strategy merge loop in sync.Rs, Config::set_options().



This issue affects RustDesk Client: through 1.4.8.

## References
- https://github.com/rustdesk/rustdesk,https://github.com/rustdesk/hbb_common
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30792.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30792
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk/releases
- https://rustdesk.com/docs/en/self-host/client-configuration/advanced-settings/
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
