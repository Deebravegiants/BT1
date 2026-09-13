# [M] Fault Injection of EdDSA signature in WolfCrypt

## Summary
Severity: Medium
Advisory: CVE-2024-2881
CVSS: 6.7 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2024-08-29
Source: https://osv.dev/vulnerability/CVE-2024-2881
Type: osv

## Details
Fault Injection vulnerability in wc_ed25519_sign_msg function in wolfssl/wolfcrypt/src/ed25519.c in WolfSSL wolfssl5.6.6 on Linux/Windows allows remote attacker co-resides in the same system with a victim process to disclose information and escalate privileges via Rowhammer fault injection to the ed25519_key structure.

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v5.7.0-stable
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2881.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2881
- https://github.com/wolfSSL/wolfssl
