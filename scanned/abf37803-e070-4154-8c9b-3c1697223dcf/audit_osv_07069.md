# [H] NGINX ngx_http_dav_module vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-2026-27654
Aliases: BIT-nginx-gateway-2026-27654, CVE-2026-27654
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-nginx-2026-27654
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.29.0 <1.29.7

## Details
NGINX Open Source and NGINX Plus have a vulnerability in the ngx_http_dav_module module that might allow an attacker to trigger a buffer overflow to the NGINX worker process; this vulnerability may result in termination of the NGINX worker process or modification of source or destination file names outside the document root. This issue affects NGINX Open Source and NGINX Plus when the configuration file uses DAV module MOVE or COPY methods, prefix location (nonregular expression location configuration), and alias directives. The integrity impact is constrained because the NGINX worker process user has low privileges and does not have access to the entire system. Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000160382
- https://nvd.nist.gov/vuln/detail/CVE-2026-27654
- https://access.redhat.com/errata/RHSA-2026:10065
- https://access.redhat.com/errata/RHSA-2026:13634
- https://access.redhat.com/errata/RHSA-2026:13680
- https://access.redhat.com/errata/RHSA-2026:13839
- https://access.redhat.com/errata/RHSA-2026:14836
- https://access.redhat.com/errata/RHSA-2026:15942
- https://access.redhat.com/errata/RHSA-2026:15943
- https://access.redhat.com/errata/RHSA-2026:15945
- https://access.redhat.com/errata/RHSA-2026:15966
- https://access.redhat.com/errata/RHSA-2026:6906
- https://access.redhat.com/errata/RHSA-2026:6907
- https://access.redhat.com/errata/RHSA-2026:6923
- https://access.redhat.com/errata/RHSA-2026:7002
- https://access.redhat.com/errata/RHSA-2026:7343
- https://access.redhat.com/errata/RHSA-2026:8346
- https://access.redhat.com/security/cve/CVE-2026-27654
- https://bugzilla.redhat.com/show_bug.cgi?id=2450776
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27654.json
