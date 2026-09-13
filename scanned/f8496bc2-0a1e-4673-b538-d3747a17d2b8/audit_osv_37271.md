# [M] RustDesk Client Accepts Pseudo-Encrypted Config Strings Without Cryptographic Validation

## Summary
Severity: Medium
Advisory: CVE-2026-30791
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-30791
Type: osv

## Details
Use of a Broken or Risky Cryptographic Algorithm vulnerability in rustdesk-client RustDesk Client rustdesk-client on Windows, MacOS, Linux, iOS, Android, WebClient (Config import, URI scheme handler, CLI --config modules) allows Retrieve Embedded Sensitive Data. This vulnerability is associated with program files flutter/lib/common.Dart, hbb_common/src/config.Rs and program routines parseRustdeskUri(), importConfig().

This issue affects RustDesk Client: through 1.4.5.

## References
- https://github.com/rustdesk/rustdesk,https://github.com/rustdesk/hbb_common
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30791.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30791
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk/releases
- https://rustdesk.com/docs/en/client/
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
