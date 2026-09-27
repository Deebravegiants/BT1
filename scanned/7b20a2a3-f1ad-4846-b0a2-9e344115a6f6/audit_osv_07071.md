# [M] NGINX ngx_mail_proxy_module vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2026-28753
Aliases: BIT-nginx-gateway-2026-28753, CVE-2026-28753
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-nginx-2026-28753
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.29.0 <1.29.7

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_mail_smtp_module module due to the improper handling of CRLF sequences in DNS responses. This allows an attacker-controlled DNS server to inject arbitrary headers into SMTP upstream requests, leading to potential request manipulation. Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000160367
- https://nvd.nist.gov/vuln/detail/CVE-2026-28753
