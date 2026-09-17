# [H] CVE-2024-24990

## Summary
Severity: High
Advisory: CVE-2024-24990
Aliases: BIT-nginx-2024-24990, BIT-nginx-gateway-2024-24990
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-14
Source: https://osv.dev/vulnerability/CVE-2024-24990
Type: osv

## Details
When NGINX Plus or NGINX OSS are configured to use the HTTP/3 QUIC module, undisclosed requests can cause NGINX worker processes to terminate.

Note: The HTTP/3 QUIC module is not enabled by default and is considered experimental. For more information, refer to  Support for QUIC and HTTP/3 https://nginx.org/en/docs/quic.html .



 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated

## References
- https://my.f5.com/manage/s/article/K000138445
- http://www.openwall.com/lists/oss-security/2024/05/30/4
