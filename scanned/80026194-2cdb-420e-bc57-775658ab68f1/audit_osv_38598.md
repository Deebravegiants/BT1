# [C] PJSIP: Stack buffer overflow in pjsip_auth_create_digest2()

## Summary
Severity: Critical
Advisory: CVE-2026-40892
Aliases: GHSA-2wcg-w3c4-48r7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40892
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. In 2.16 and earlier, a stack buffer overflow exists in pjsip_auth_create_digest2() in PJSIP when using pre-computed digest credentials (PJSIP_CRED_DATA_DIGEST). The function copies credential data using cred_info->data.slen as the length without an upper-bound check, which can overflow the fixed-size ha1 stack buffer (128 bytes) if data.slen exceeds the expected digest string length.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40892.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-2wcg-w3c4-48r7
- https://nvd.nist.gov/vuln/detail/CVE-2026-40892
- https://github.com/pjsip/pjproject/commit/c82123ea6f3c3652bbc9ebd5e9e658c301451687
