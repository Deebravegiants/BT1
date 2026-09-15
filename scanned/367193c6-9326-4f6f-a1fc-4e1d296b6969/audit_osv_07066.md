# [M] NGINX ngx_mail_smtp_module vulnerability

## Summary
Severity: Medium
Advisory: BIT-nginx-2025-53859
Aliases: BIT-nginx-gateway-2025-53859, CVE-2025-53859
Ecosystem: Bitnami
Published: 2025-08-18
Source: https://osv.dev/vulnerability/BIT-nginx-2025-53859
Type: osv

## Affected
- Bitnami: `nginx` — affected >=0.7.0 <1.29.1

## Details
NGINX Open Source and NGINX Plus have a vulnerability in the ngx_mail_smtp_module that might allow an unauthenticated attacker to over-read NGINX SMTP authentication process memory; as a result, the server side may leak arbitrary bytes sent in a request to the authentication server. This issue happens during the NGINX SMTP authentication process and requires the attacker to make preparations against the target system to extract the leaked data. The issue affects NGINX only if (1) it is built with the ngx_mail_smtp_module, (2) the smtp_auth directive is configured with method "none," and (3) the authentication server returns the "Auth-Wait" response header.




Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000152786
- https://nvd.nist.gov/vuln/detail/CVE-2025-53859
- http://www.openwall.com/lists/oss-security/2025/08/13/5
