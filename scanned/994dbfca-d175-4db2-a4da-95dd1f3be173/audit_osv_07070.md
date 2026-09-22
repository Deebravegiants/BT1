# [H] NGINX ngx_http_mp4_module vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-2026-27784
Aliases: BIT-nginx-gateway-2026-27784, CVE-2026-27784
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-nginx-2026-27784
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.29.0 <1.29.7

## Details
The 32-bit implementation of NGINX Open Source has a vulnerability in the ngx_http_mp4_module module, which might allow an attacker to over-read or over-write NGINX worker memory resulting in its termination, using a specially crafted MP4 file. The issue only affects 32-bit NGINX Open Source if it is built with the ngx_http_mp4_module module and the mp4 directive is used in the configuration file. Additionally, the attack is possible only if an attacker can trigger the processing of a specially crafted MP4 file with the ngx_http_mp4_module module. 


Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000160364
- https://nvd.nist.gov/vuln/detail/CVE-2026-27784
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
- https://access.redhat.com/security/cve/CVE-2026-27784
- https://bugzilla.redhat.com/show_bug.cgi?id=2450785
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27784.json
