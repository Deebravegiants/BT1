# [H] ALPINE-CVE-2019-1543

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-1543
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.4 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-03-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1543
Type: osv

## Affected
- Alpine:v3.10: `file` — affected >=0 <5.36-r0
- Alpine:v3.11: `file` — affected >=0 <5.36-r0
- Alpine:v3.12: `file` — affected >=0 <5.36-r0
- Alpine:v3.13: `file` — affected >=0 <5.36-r0
- Alpine:v3.14: `file` — affected >=0 <5.36-r0
- Alpine:v3.15: `file` — affected >=0 <5.36-r0
- Alpine:v3.16: `file` — affected >=0 <5.36-r0
- Alpine:v3.17: `file` — affected >=0 <5.36-r0
- Alpine:v3.18: `file` — affected >=0 <5.36-r0
- Alpine:v3.19: `file` — affected >=0 <5.36-r0
- Alpine:v3.20: `file` — affected >=0 <5.36-r0
- Alpine:v3.21: `file` — affected >=0 <5.36-r0
- Alpine:v3.22: `file` — affected >=0 <5.36-r0
- Alpine:v3.23: `file` — affected >=0 <5.36-r0
- Alpine:v3.24: `file` — affected >=0 <5.36-r0
- Alpine:v3.10: `openssl` — affected >=1.1.0 <1.1.1b-r1
- Alpine:v3.11: `openssl` — affected >=1.1.0 <1.1.1b-r1
- Alpine:v3.12: `openssl` — affected >=1.1.0 <1.1.1b-r1
- Alpine:v3.13: `openssl` — affected >=1.1.0 <1.1.1b-r1
- Alpine:v3.14: `openssl` — affected >=1.1.0 <1.1.1b-r1
- Alpine:v3.15: `openssl` — affected >=1.1.0 <1.1.1b-r1
- Alpine:v3.16: `openssl` — affected >=1.1.0 <1.1.1b-r1
- Alpine:v3.17: `openssl` — affected >=1.1.0 <1.1.1b-r1
- Alpine:v3.18: `openssl` — affected >=1.1.0 <1.1.1b-r1
- Alpine:v3.19: `openssl` — affected >=1.1.0 <1.1.1b-r1

## Details
ChaCha20-Poly1305 is an AEAD cipher, and requires a unique nonce input for every encryption operation. RFC 7539 specifies that the nonce value (IV) should be 96 bits (12 bytes). OpenSSL allows a variable nonce length and front pads the nonce with 0 bytes if it is less than 12 bytes. However it also incorrectly allows a nonce to be set of up to 16 bytes. In this case only the last 12 bytes are significant and any additional leading bytes are ignored. It is a requirement of using this cipher that nonce values are unique. Messages encrypted using a reused nonce value are susceptible to serious confidentiality and integrity attacks. If an application changes the default nonce length to be longer than 12 bytes and then makes a change to the leading bytes of the nonce expecting the new value to be a new unique nonce then such an application could inadvertently encrypt messages with a reused nonce. Additionally the ignored bytes in a long nonce are not covered by the integrity guarantee of this cipher. Any application that relies on the integrity of these ignored leading bytes of a long nonce may be further affected. Any OpenSSL internal use of this cipher, including in SSL/TLS, is safe because no such use sets such a long nonce value. However user applications that use this cipher directly and set a non-default nonce length to be longer than 12 bytes may be vulnerable. OpenSSL versions 1.1.1 and 1.1.0 are affected by this issue. Due to the limited scope of affected deployments this has been assessed as low severity and therefore we are not creating new releases at this time. Fixed in OpenSSL 1.1.1c (Affected 1.1.1-1.1.1b). Fixed in OpenSSL 1.1.0k (Affected 1.1.0-1.1.0j).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1543
