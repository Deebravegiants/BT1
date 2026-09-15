# [H] NGINX ngx_mail_auth_http_module vulnerability

## Summary
Severity: High
Advisory: BIT-nginx-2026-27651
Aliases: BIT-nginx-gateway-2026-27651, CVE-2026-27651
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-nginx-2026-27651
Type: osv

## Affected
- Bitnami: `nginx` — affected >=1.29.0 <1.29.7

## Details
When the ngx_mail_auth_http_module module is enabled on NGINX Plus or NGINX Open Source, undisclosed requests can cause worker processes to terminate. This issue may occur when (1) CRAM-MD5 or APOP authentication is enabled, and (2) the authentication server permits retry by returning the Auth-Wait response header. Note: Software versions which have reached End of Technical Support (EoTS) are not evaluated.

## References
- https://my.f5.com/manage/s/article/K000160383
- https://nvd.nist.gov/vuln/detail/CVE-2026-27651
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
- https://access.redhat.com/security/cve/CVE-2026-27651
- https://bugzilla.redhat.com/show_bug.cgi?id=2450791
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27651.json
