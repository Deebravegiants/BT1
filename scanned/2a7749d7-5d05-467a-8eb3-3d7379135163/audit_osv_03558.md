# [M] ALPINE-CVE-2026-28755

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-28755
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28755
Type: osv

## Affected
- Alpine:v3.22: `nginx` — affected >=0 <1.28.3-r0
- Alpine:v3.23: `nginx` — affected >=0 <1.28.3-r0
- Alpine:v3.24: `nginx` — affected >=0 <1.28.3-r0

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_stream_ssl_module module due to the improper handling of revoked certificates when configured with the ssl_verify_client on and ssl_ocsp on directives, allowing the TLS handshake to succeed even after an OCSP check identifies the certificate as revoked.   


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28755
