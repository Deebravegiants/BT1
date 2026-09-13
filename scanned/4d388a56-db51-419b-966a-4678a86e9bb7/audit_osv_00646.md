# [M] ALPINE-CVE-2017-3737

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3737
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3737
Type: osv

## Affected
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2n-r0
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2n-r0
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2n-r0
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2n-r0
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2n-r0
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2n-r0

## Details
OpenSSL 1.0.2 (starting from version 1.0.2b) introduced an "error state" mechanism. The intent was that if a fatal error occurred during a handshake then OpenSSL would move into the error state and would immediately fail if you attempted to continue the handshake. This works as designed for the explicit handshake functions (SSL_do_handshake(), SSL_accept() and SSL_connect()), however due to a bug it does not work correctly if SSL_read() or SSL_write() is called directly. In that scenario, if the handshake fails then a fatal error will be returned in the initial function call. If SSL_read()/SSL_write() is subsequently called by the application for the same SSL object then it will succeed and the data is passed without being decrypted/encrypted directly from the SSL/TLS record layer. In order to exploit this issue an application bug would have to be present that resulted in a call to SSL_read()/SSL_write() being issued after having already received a fatal error. OpenSSL version 1.0.2b-1.0.2m are affected. Fixed in OpenSSL 1.0.2n. OpenSSL 1.1.0 is not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3737
