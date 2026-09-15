# [H] ALPINE-CVE-2017-3731

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-3731
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3731
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2k-r0
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2k-r0
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2k-r0

## Details
If an SSL/TLS server or client is running on a 32-bit host, and a specific cipher is being used, then a truncated packet can cause that server or client to perform an out-of-bounds read, usually resulting in a crash. For OpenSSL 1.1.0, the crash can be triggered when using CHACHA20/POLY1305; users should upgrade to 1.1.0d. For Openssl 1.0.2, the crash can be triggered when using RC4-MD5; users who have not disabled that algorithm should update to 1.0.2k.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3731
