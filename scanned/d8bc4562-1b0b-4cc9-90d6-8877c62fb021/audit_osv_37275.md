# [H] RustDesk rustdesk://config/ URI Silently Re-homes Client to Attacker-Controlled Server

## Summary
Severity: High
Advisory: CVE-2026-30797
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-30797
Type: osv

## Details
Missing Authorization vulnerability in rustdesk-client RustDesk Client rustdesk-client on Windows, MacOS, Linux, iOS, Android (Flutter URI scheme handler, config import modules) allows Application API Message Manipulation via Man-in-the-Middle. This vulnerability is associated with program files flutter/lib/common.Dart and program routines importConfig() via URI handler.

This issue affects RustDesk Client: through 1.4.5.

## References
- https://github.com/rustdesk/rustdesk,https://github.com/rustdesk/hbb_common
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30797.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30797
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk/releases
- https://rustdesk.com/docs/en/client/
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
