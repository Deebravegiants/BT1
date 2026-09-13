# [M] ALPINE-CVE-2019-1559

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-1559
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1559
Type: osv

## Affected
- Alpine:v3.6: `openssl` — affected >=1.0.2 <1.0.2r-r0
- Alpine:v3.7: `openssl` — affected >=1.0.2 <1.0.2r-r0
- Alpine:v3.8: `openssl` — affected >=1.0.2 <1.0.2r-r0

## Details
If an application encounters a fatal protocol error and then calls SSL_shutdown() twice (once to send a close_notify, and once to receive one) then OpenSSL can respond differently to the calling application if a 0 byte record is received with invalid padding compared to if a 0 byte record is received with an invalid MAC. If the application then behaves differently based on that in a way that is detectable to the remote peer, then this amounts to a padding oracle that could be used to decrypt data. In order for this to be exploitable "non-stitched" ciphersuites must be in use. Stitched ciphersuites are optimised implementations of certain commonly used ciphersuites. Also the application must call SSL_shutdown() twice even if a protocol error has occurred (applications should not do this but some do anyway). Fixed in OpenSSL 1.0.2r (Affected 1.0.2-1.0.2q).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1559
