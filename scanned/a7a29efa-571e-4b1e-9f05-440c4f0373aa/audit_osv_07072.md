# [M] NGINX ngx_stream_ssl_module vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2026-28755
Aliases: BIT-nginx-gateway-2026-28755, CVE-2026-28755
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-nginx-2026-28755
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.29.0 <1.29.7

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_stream_ssl_module module due to the improper handling of revoked certificates when configured with the ssl_verify_client on and ssl_ocsp on directives, allowing the TLS handshake to succeed even after an OCSP check identifies the certificate as revoked.   


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000160368
- https://nvd.nist.gov/vuln/detail/CVE-2026-28755
