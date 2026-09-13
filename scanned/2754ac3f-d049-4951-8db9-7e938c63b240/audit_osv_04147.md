# [H] Apache APISIX: Openid-connect `tls_verify` field is disabled by default

## Summary
Severity: High
Advisory: BIT-apisix-2026-31923
Aliases: CVE-2026-31923
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-apisix-2026-31923
Type: osv

## Affected
- Bitnami: `apisix` — affected >=0.7.0 <3.16.0

## Details
Cleartext Transmission of Sensitive Information vulnerability in Apache APISIX.

This can occur due to `ssl_verify` in openid-connect plugin configuration being set to false by default.
This issue affects Apache APISIX: from 0.7 through 3.15.0.

Users are recommended to upgrade to version 3.16.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/04/14/1
- https://lists.apache.org/thread/0pjs72l7qj83j3srw1l1toyj24bsgkds
- https://nvd.nist.gov/vuln/detail/CVE-2026-31923
