# [C] NGINX ngx_http_rewrite_module vulnerability

## Summary
Severity: Critical
Advisory: BIT-nginx-2026-9256
Aliases: BIT-nginx-gateway-2026-9256, CVE-2026-9256
Ecosystem: Bitnami
Published: 2026-06-01
Source: https://osv.dev/vulnerability/BIT-nginx-2026-9256
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.31.0 <1.31.1

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_rewrite_module module. This vulnerability exists when a rewrite directive uses a regex pattern with distinct, overlapping Perl-Compatible Regular Expression (PCRE) captures (for example, ^/((.*))$) and a replacement string that references multiple such captures (for example, $1$2) in a redirect or arguments context. An unauthenticated attacker along with conditions beyond their control can exploit this vulnerability by sending crafted HTTP requests. This may cause a heap buffer overflow in the NGINX worker process leading to a restart. Additionally, attackers can execute code on systems with Address Space Layout Randomization (ASLR) disabled or when the attacker can bypass ASLR. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- http://www.openwall.com/lists/oss-security/2026/05/22/14
- https://my.f5.com/manage/s/article/K000161377
- https://nvd.nist.gov/vuln/detail/CVE-2026-9256
- https://lists.debian.org/debian-lts-announce/2026/06/msg00023.html
- https://access.redhat.com/errata/RHSA-2026:20351
- https://access.redhat.com/errata/RHSA-2026:28212
- https://access.redhat.com/errata/RHSA-2026:28921
- https://access.redhat.com/errata/RHSA-2026:28973
- https://access.redhat.com/errata/RHSA-2026:29151
- https://access.redhat.com/errata/RHSA-2026:29874
- https://access.redhat.com/errata/RHSA-2026:33313
- https://access.redhat.com/security/cve/CVE-2026-9256
- https://bugzilla.redhat.com/show_bug.cgi?id=2480746
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-9256.json
- https://access.redhat.com/errata/RHSA-2026:44481
- https://access.redhat.com/errata/RHSA-2026:58981
