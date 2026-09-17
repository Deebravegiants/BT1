# [C] ALPINE-CVE-2026-40892

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-40892
Ecosystem: Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40892
Type: osv

## Affected
- Alpine:v3.24: `pjproject` — affected >=0 <2.17-r0

## Details
PJSIP is a free and open source multimedia communication library written in C. In 2.16 and earlier, a stack buffer overflow exists in pjsip_auth_create_digest2() in PJSIP when using pre-computed digest credentials (PJSIP_CRED_DATA_DIGEST). The function copies credential data using cred_info->data.slen as the length without an upper-bound check, which can overflow the fixed-size ha1 stack buffer (128 bytes) if data.slen exceeds the expected digest string length.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40892
