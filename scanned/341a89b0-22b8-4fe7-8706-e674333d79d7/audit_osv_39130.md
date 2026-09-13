# [H] Coturn: Stack buffer overflow in decode_oauth_token_gcm()

## Summary
Severity: High
Advisory: CVE-2026-43994
Aliases: GHSA-74pg-rfh2-5qw5
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-43994
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Versions prior to 4.10.0 contain a stack buffer overflow in decode_oauth_token_gcm(). A uint16_t nonce_len field read from an attacker-supplied OAuth access token (0-65535) is passed directly to memcpy() as the copy length into a 256-byte stack buffer (oauth_encrypted_block.nonce[256]) without bounds checking. The overflow occurs before AES-GCM authentication is verified, the attacker does not need to know the OAuth key or produce a valid AES-GCM token. Up to 735 bytes of attacker-controlled data are written past the buffer, may corrupt adjacent stack data, including control-flow data depending on compiler, ABI, and mitigations. Requires --oauth mode (non-default). This may provide a plausible RCE primitive depending on exploit mitigations; because coturn is widely deployed for WebRTC TURN/STUN and --oauth is commonly recommended, impact can be broad. This issue has been fixed in version 4.10.0.

## References
- https://github.com/coturn/coturn/releases/tag/4.10.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43994.json
- https://github.com/coturn/coturn/security/advisories/GHSA-74pg-rfh2-5qw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-43994
