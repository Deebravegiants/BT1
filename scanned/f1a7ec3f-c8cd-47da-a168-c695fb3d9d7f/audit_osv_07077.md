# [C] NGINX Open-Source ngx_http_v3_module vulnerability

## Summary
Severity: Critical
Advisory: BIT-nginx-2026-42530
Aliases: BIT-nginx-gateway-2026-42530, CVE-2026-42530
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-nginx-2026-42530
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.31.0 <1.31.2

## Details
NGINX Open Source has a vulnerability in the ngx_http_v3_module module. When NGINX Open Source is configured to use the HTTP/3 QUIC module, a remote unauthenticated attacker along with conditions beyond their control can use a specially crafted HTTP/3 session to reopen a QPACK encoder stream. This may cause a Use-after-Free in the NGINX worker process leading to a restart. Additionally, attackers can execute code on systems with Address Space Layout Randomization (ASLR) disabled or when the attacker can bypass ASLR.  


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000161616
- https://nvd.nist.gov/vuln/detail/CVE-2026-42530
- https://access.redhat.com/security/cve/CVE-2026-42530
- https://bugzilla.redhat.com/show_bug.cgi?id=2489872
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42530.json
- https://access.redhat.com/errata/RHSA-2026:20351
