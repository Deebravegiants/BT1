# [H] NGINX ngx_http_mp4_module vulnerability CVE-2022-41742

## Summary
Severity: High
Advisory: BIT-nginx-2022-41742
Aliases: BIT-nginx-ingress-controller-2022-41742, CVE-2022-41742
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-nginx-2022-41742
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.23.0 <1.23.2

## Details
NGINX Open Source before versions 1.23.2 and 1.22.1, NGINX Open Source Subscription before versions R2 P1 and R1 P1, and NGINX Plus before versions R27 P1 and R26 P1 have a vulnerability in the module ngx_http_mp4_module that might allow a local attacker to cause a worker process crash, or might result in worker process memory disclosure by using a specially crafted audio or video file. The issue affects only NGINX products that are built with the module ngx_http_mp4_module, when the mp4 directive is used in the configuration file. Further, the attack is possible only if an attacker can trigger processing of a specially crafted audio or video file with the module ngx_http_mp4_module.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00031.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BPRVYA4FS34VWB4FEFYNAD7Z2LFCJVEI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FD6M3PVVKO35WLAA7GLDBS6TEQ26SM64/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WBORRVG7VVXYOAIAD64ZHES2U2VIUKFQ/
- https://security.netapp.com/advisory/ntap-20230120-0005/
- https://support.f5.com/csp/article/K28112382
- https://www.debian.org/security/2022/dsa-5281
- https://nvd.nist.gov/vuln/detail/CVE-2022-41742
