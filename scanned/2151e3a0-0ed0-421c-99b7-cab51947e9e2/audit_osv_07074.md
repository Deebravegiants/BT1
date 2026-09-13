# [M] NGINX ngx_quic_module vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2026-40460
Aliases: BIT-nginx-gateway-2026-40460, CVE-2026-40460
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-nginx-2026-40460
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.26.0 <1.30.1

## Details
When NGINX Plus or NGINX Open Source are configured to use the HTTP/3 QUIC module, an attacker may be able to spoof their source IP address allowing for bypass of authorization or bypass of rate limiting.  Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161068
- https://nvd.nist.gov/vuln/detail/CVE-2026-40460
