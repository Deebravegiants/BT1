# [C] ALPINE-CVE-2026-56123

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-56123
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56123
Type: osv

## Affected
- Alpine:v3.21: `socat` — affected >=1.8.0.0 <1.8.1.2-r0
- Alpine:v3.22: `socat` — affected >=1.8.0.0 <1.8.1.2-r0
- Alpine:v3.23: `socat` — affected >=1.8.0.0 <1.8.1.2-r0
- Alpine:v3.24: `socat` — affected >=1.8.0.0 <1.8.1.2-r0

## Details
socat versions 1.8.0.0 through 1.8.1.1 contain a heap-based buffer overflow vulnerability that allows a malicious SOCKS5 proxy server to overwrite adjacent heap memory by exploiting a sign-extension flaw in the DOMAINNAME reply parser. During connection setup, the domain name length byte is read through a signed char field causing a negative bytes_to_read value that is implicitly converted to size_t, resulting in an unbounded heap write into the 262-byte reply buffer with attacker-controlled size and content.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56123
