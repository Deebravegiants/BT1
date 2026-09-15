# [H] BIT-nginx-2026-1642

## Summary
Severity: High
Advisory: BIT-nginx-2026-1642
Aliases: BIT-nginx-gateway-2026-1642, CVE-2026-1642
Ecosystem: Bitnami
Published: 2026-02-10
Source: https://osv.dev/vulnerability/BIT-nginx-2026-1642
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.29.4 <1.29.5

## Details
A vulnerability exists in NGINX OSS and NGINX Plus when configured to proxy to upstream Transport Layer Security (TLS) servers. An attacker with a man-in-the-middle (MITM) position on the upstream server side—along with conditions beyond the attacker's control—may be able to inject plain text data into the response from an upstream proxied server. Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1642
- https://my.f5.com/manage/s/article/K000159824
- http://www.openwall.com/lists/oss-security/2026/02/05/1
