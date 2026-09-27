# [C] Apache APISIX: Authentication bypass in jwe-decrypt

## Summary
Severity: Critical
Advisory: BIT-apisix-2026-49230
Aliases: CVE-2026-49230
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-apisix-2026-49230
Type: osv

## Affected
- Bitnami: `apisix` — affected >=3.8.0 <3.17.0

## Details
Improper Validation of Integrity Check Value vulnerability in Apache APISIX.

The jwe-decrypt plugin under default configuration is vulnerable to authentication bypass. 
This issue affects Apache APISIX: from 3.8.0 through 3.16.0.

Users are recommended to upgrade to version 3.17.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/19/12
- https://lists.apache.org/thread/n0blgkpvz38ghh5rrh6wtl476919xj1b
- https://nvd.nist.gov/vuln/detail/CVE-2026-49230
