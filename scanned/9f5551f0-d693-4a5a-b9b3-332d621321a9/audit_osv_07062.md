# [H] NGINX HTTP/3 QUIC vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-2024-24989
Aliases: BIT-nginx-gateway-2024-24989, CVE-2024-24989
Ecosystem: Bitnami
Published: 2024-06-04
Source: https://osv.dev/vulnerability/BIT-nginx-2024-24989
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.25.3 <1.25.4

## Details
When NGINX Plus or NGINX OSS are configured to use the HTTP/3 QUIC module, undisclosed requests can cause NGINX worker processes to terminate.

Note: The HTTP/3 QUIC module is not enabled by default and is considered experimental. For more information, refer to  Support for QUIC and HTTP/3 https://nginx.org/en/docs/quic.html .



NOTE: Software versions which have reached End of Technical Support (EoTS) are not evaluated

## References
- https://my.f5.com/manage/s/article/K000138444
- http://www.openwall.com/lists/oss-security/2024/05/30/4
- https://nvd.nist.gov/vuln/detail/CVE-2024-24989
