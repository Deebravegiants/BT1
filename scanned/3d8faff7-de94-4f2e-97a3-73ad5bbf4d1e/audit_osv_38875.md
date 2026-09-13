# [C] Neat VNC: Buffer overflow due to oversized RSA public keys

## Summary
Severity: Critical
Advisory: CVE-2026-42859
Aliases: GHSA-567c-gpv8-qh9h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42859
Type: osv

## Details
Neat VNC is a VNC server library. Prior to 0.9.6, a pre-authentication stack buffer overflow exists in neatvnc in the RSA-AES security type handler. An unauthenticated remote attacker who can reach the VNC listening socket can send a crafted security type 5 (RSA-AES) or security type 129 (RSA-AES-256) handshake with an oversized client RSA public key, causing rsa_aes_send_challenge in src/auth/rsa-aes.c to overflow a 1024-byte on-stack buffer when encrypting the server challenge. This results in at least a denial of service via server crash. This vulnerability is fixed in 0.9.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42859.json
- https://github.com/any1/neatvnc/security/advisories/GHSA-567c-gpv8-qh9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-42859
- https://github.com/any1/neatvnc/commit/1f6cd6b75cc167fed3a19a9d1552a1f662f6b337
