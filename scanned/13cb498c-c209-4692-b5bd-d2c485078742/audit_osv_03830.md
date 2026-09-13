# [H] ALPINE-CVE-2026-55199

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-55199
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-55199
Type: osv

## Affected
- Alpine:v3.21: `libssh2` — affected >=0 <1.11.1-r2
- Alpine:v3.22: `libssh2` — affected >=0 <1.11.1-r2
- Alpine:v3.23: `libssh2` — affected >=0 <1.11.1-r3
- Alpine:v3.24: `libssh2` — affected >=0 <1.11.1-r3
- Alpine:v3.24: `rust` — affected >=0 <1.96.1-r0

## Details
libssh2 through 1.11.1, fixed in commit 1762685, contains a pre-authentication denial of service vulnerability in the SSH_MSG_EXT_INFO handler in src/packet.c that allows a malicious SSH server to cause a client CPU exhaustion loop by sending a crafted extension count value. A malicious server can set nr_extensions to 0xFFFFFFFF during key exchange, causing the client to spin in a tight CPU loop for over 60 seconds because return values from _libssh2_get_string() are unchecked and the session timeout does not apply to CPU-bound loops.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-55199
