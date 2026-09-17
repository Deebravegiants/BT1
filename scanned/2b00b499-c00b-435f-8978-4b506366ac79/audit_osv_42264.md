# [M] libssh2 Integer Underflow DoS via AES-GCM Cipher Negotiation

## Summary
Severity: Medium
Advisory: CVE-2026-66033
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66033
Type: osv

## Details
libssh2 through 1.11.1, fixed in commit a2ed82d, contains a pre-authentication integer underflow vulnerability in the ssh2_cipher_crypt() function in src/openssl.c that allows a malicious SSH server to crash any connecting client by negotiating AES-GCM ciphers during handshake. Attackers can exploit the underflow in the expression computing blocksize minus aadlen minus authentication tag length to trigger an out-of-bounds read and a memcpy call with a near-SIZE_MAX length argument, causing immediate process crash before any authentication occurs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66033.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66033
- https://www.vulncheck.com/advisories/libssh2-integer-underflow-dos-via-aes-gcm-cipher-negotiation
- https://github.com/libssh2/libssh2/commit/a2ed82d40964bbc0d64cd717aa0a5a892117d2e6
- https://github.com/libssh2/libssh2/pull/2401
- https://github.com/libssh2/libssh2
