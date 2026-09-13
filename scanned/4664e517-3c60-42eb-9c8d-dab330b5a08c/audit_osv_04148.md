# [M] Apache APISIX: Plugin tencent-cloud-cls log export uses plaintext HTTP

## Summary
Severity: Medium
Advisory: BIT-apisix-2026-31924
Aliases: CVE-2026-31924
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-apisix-2026-31924
Type: osv

## Affected
- Bitnami: `apisix` — affected >=2.99.0 <3.16.0

## Details
Cleartext Transmission of Sensitive Information vulnerability in Apache APISIX.

tencent-cloud-cls log export uses plaintext HTTP
This issue affects Apache APISIX: from 2.99.0 through 3.15.0.

Users are recommended to upgrade to version 3.16.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/04/14/2
- https://lists.apache.org/thread/sqxjjlt87c1q28db28ztdxylm5pgwohq
- https://nvd.nist.gov/vuln/detail/CVE-2026-31924
