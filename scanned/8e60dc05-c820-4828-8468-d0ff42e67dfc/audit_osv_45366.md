# [M] libssh2 through 1.11.1, fixed in commit a2ed82d, contains a pre-authentication integer underflow...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1086
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/JLSEC-2026-1086
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.11.104+0

## Details
libssh2 through 1.11.1, fixed in commit a2ed82d, contains a pre-authentication integer underflow vulnerability in the `ssh2_cipher_crypt()` function in `src/openssl.c` that allows a malicious SSH server to crash any connecting client by negotiating AES-GCM ciphers during handshake. Attackers can exploit the underflow in the expression computing blocksize minus aadlen minus authentication tag length to trigger an out-of-bounds read and a memcpy call with a `near-SIZE_MAX` length argument, causing immediate process crash before any authentication occurs.

## References
- https://github.com/advisories/GHSA-2g8c-wcg8-r65c
- https://github.com/libssh2/libssh2/commit/a2ed82d40964bbc0d64cd717aa0a5a892117d2e6
- https://github.com/libssh2/libssh2/pull/2401
- https://nvd.nist.gov/vuln/detail/CVE-2026-66033
- https://www.vulncheck.com/advisories/libssh2-integer-underflow-dos-via-aes-gcm-cipher-negotiation
