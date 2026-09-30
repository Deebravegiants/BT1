# [H] BIT-nginx-ingress-controller-2022-41743

## Summary
Severity: High
Advisory: BIT-nginx-ingress-controller-2022-41743
Aliases: CVE-2022-41743
Ecosystem: Bitnami
Published: 2023-11-06
Source: https://osv.dev/vulnerability/BIT-nginx-ingress-controller-2022-41743
Type: osv

## Affected
- Bitnami: `nginx-ingress-controller` — affected >=2.0.0 <2.4.0

## Details
NGINX Plus before versions R27 P1 and R26 P1 have a vulnerability in the module ngx_http_hls_module that might allow a local attacker to corrupt NGINX worker memory, resulting in its crash or potential other impact using a specially crafted audio or video file. The issue affects only NGINX Plus when the hls directive is used in the configuration file. Further, the attack is possible only if an attacker can trigger processing of a specially crafted audio or video file with the module ngx_http_hls_module.

## References
- https://support.f5.com/csp/article/K01112063
