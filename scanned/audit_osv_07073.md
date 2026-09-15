# [H] NGINX ngx_http_mp4_module vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-2026-32647
Aliases: BIT-nginx-gateway-2026-32647, CVE-2026-32647
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-nginx-2026-32647
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.29.0 <1.29.7

## Details
NGINX Open Source and NGINX Plus have a vulnerability in the ngx_http_mp4_module module, which might allow an attacker to trigger a buffer over-read or over-write to the NGINX worker memory resulting in its termination or possibly code execution, using a specially crafted MP4 file. This issue affects NGINX Open Source and NGINX Plus if it is built with the ngx_http_mp4_module module and the mp4 directive is used in the configuration file. Additionally, the attack is possible only if an attacker can trigger the processing of a specially crafted MP4 file with the ngx_http_mp4_module module. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000160366
- https://nvd.nist.gov/vuln/detail/CVE-2026-32647
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
- https://access.redhat.com/security/cve/CVE-2026-32647
- https://bugzilla.redhat.com/show_bug.cgi?id=2449598
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-32647.json
