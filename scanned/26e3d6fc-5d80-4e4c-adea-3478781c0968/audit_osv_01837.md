# [M] ALPINE-CVE-2020-1730

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-1730
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2020-04-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1730
Type: osv

## Affected
- Alpine:v3.10: `libssh` — affected >=0.8.0 <0.8.9-r0
- Alpine:v3.11: `libssh` — affected >=0.8.0 <0.9.4-r0
- Alpine:v3.9: `libssh` — affected >=0.8.0 <0.7.6-r3

## Details
A flaw was found in libssh versions before 0.8.9 and before 0.9.4 in the way it handled AES-CTR (or DES ciphers if enabled) ciphers. The server or client could crash when the connection hasn't been fully initialized and the system tries to cleanup the ciphers when closing the connection. The biggest threat from this vulnerability is system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1730
