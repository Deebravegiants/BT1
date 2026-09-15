# [H] CryptoLib vulnerable to Stack Buffer Overflow in Crypto_Key_Update due to missing TLV length check

## Summary
Severity: High
Advisory: CVE-2025-64096
Aliases: GHSA-w6c3-pxvr-6m6j
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-64096
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. Prior to 1.4.2, there is a missing bounds check in Crypto_Key_update() (crypto_key_mgmt.c) which allows a remote attacker to trigger a stack-based buffer overflow by supplying a TLV packet with a spoofed length field. The function calculates the number of keys from an attacker-controlled field (pdu_len), which may exceed the static array size (kblk[98]), leading to an out-of-bounds write and potential memory corruption. This vulnerability is fixed in 1.4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64096.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-w6c3-pxvr-6m6j
- https://nvd.nist.gov/vuln/detail/CVE-2025-64096
