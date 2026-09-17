# [M] NGINX MP4 module vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2024-7347
Aliases: BIT-nginx-gateway-2024-7347, CVE-2024-7347
Ecosystem: Bitnami
Published: 2024-08-16
Source: https://osv.dev/vulnerability/BIT-nginx-2024-7347
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.27.0 <1.27.1

## Details
NGINX Open Source and NGINX Plus have a vulnerability in the ngx_http_mp4_module, which might allow an attacker to over-read NGINX worker memory resulting in its termination, using a specially crafted mp4 file. The issue only affects NGINX if it is built with the ngx_http_mp4_module and the mp4 directive is used in the configuration file. Additionally, the attack is possible only if an attacker can trigger the processing of a specially crafted mp4 file with the ngx_http_mp4_module.  Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000140529
- http://www.openwall.com/lists/oss-security/2024/08/14/4
- https://nvd.nist.gov/vuln/detail/CVE-2024-7347
- https://lists.debian.org/debian-lts-announce/2025/03/msg00017.html
