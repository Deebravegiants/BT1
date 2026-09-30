# [M] RustDesk Encrypts Local Passwords with World-Readable Machine ID and Fixed Zero Nonce (XSalsa20-Poly1305)

## Summary
Severity: Medium
Advisory: CVE-2026-30785
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-30785
Type: osv

## Details
Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution'), Use of Password Hash With Insufficient Computational Effort vulnerability in rustdesk-client RustDesk Client rustdesk, hbb_common on Windows, MacOS, Linux (Password security module, config encryption, machine UID modules) allows Retrieve Embedded Sensitive Data. This vulnerability is associated with program files hbb_common/src/password_security.Rs, hbb_common/src/config.Rs, hbb_common/src/lib.Rs (get_uuid), machine-uid/src/lib.Rs and program routines symmetric_crypt(), encrypt_str_or_original(), decrypt_str_or_original(), get_uuid(), get_machine_id().

This issue affects RustDesk Client: through 1.4.5.

## References
- https://github.com/rustdesk/hbb_common,https://github.com/rustdesk-org/machine-uid
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30785.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30785
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk/releases
- https://github.com/rustdesk/rustdesk/discussions/4979
- https://github.com/rustdesk/rustdesk/discussions/9229
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
