# [C] NGINX ngx_http_rewrite_module vulnerability

## Summary
Severity: Critical
Advisory: BIT-nginx-2026-42945
Aliases: BIT-nginx-gateway-2026-42945, CVE-2026-42945
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-nginx-2026-42945
Type: osv

## Affected
- Bitnami: `nginx` — affected >=0.6.27 <1.30.1

## Details
NGINX Plus and NGINX Open Source have a vulnerability in the ngx_http_rewrite_module module. This vulnerability exists when the rewrite directive is followed by a rewrite, if, or set directive and an unnamed Perl-Compatible Regular Expression (PCRE) capture (for example, $1, $2) with a replacement string that includes a question mark (?). An unauthenticated attacker along with conditions beyond its control can exploit this vulnerability by sending crafted HTTP requests. This may cause a heap buffer overflow in the NGINX worker process leading to a restart. Additionally, attackers can execute code on systems with Address Space Layout Randomization (ASLR) disabled or when the attacker can bypass ASLR.  Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://depthfirst.com/nginx-rift
- https://github.com/DepthFirstDisclosures/Nginx-Rift
- https://my.f5.com/manage/s/article/K000161019
- https://nvd.nist.gov/vuln/detail/CVE-2026-42945
- https://access.redhat.com/errata/RHSA-2026:17417
- https://access.redhat.com/errata/RHSA-2026:17751
- https://access.redhat.com/errata/RHSA-2026:17752
- https://access.redhat.com/errata/RHSA-2026:17753
- https://access.redhat.com/errata/RHSA-2026:17790
- https://access.redhat.com/errata/RHSA-2026:17791
- https://access.redhat.com/errata/RHSA-2026:17792
- https://access.redhat.com/errata/RHSA-2026:17793
- https://access.redhat.com/errata/RHSA-2026:17794
- https://access.redhat.com/errata/RHSA-2026:18029
- https://access.redhat.com/errata/RHSA-2026:18041
- https://access.redhat.com/errata/RHSA-2026:18063
- https://access.redhat.com/errata/RHSA-2026:19159
- https://access.redhat.com/errata/RHSA-2026:19371
- https://access.redhat.com/errata/RHSA-2026:19372
- https://access.redhat.com/errata/RHSA-2026:19374
