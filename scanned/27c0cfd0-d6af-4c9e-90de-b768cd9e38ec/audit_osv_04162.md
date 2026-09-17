# [H] Apache APISIX: Unauthenticated CPU-exhaustion DoS

## Summary
Severity: High
Advisory: BIT-apisix-2026-75005
Aliases: CVE-2026-75005
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-apisix-2026-75005
Type: osv

## Affected
- Bitnami: `apisix` — affected >=3.17.0 <3.18.0

## Details
Inefficient Algorithmic Complexity vulnerability in Apache APISIX.

 A single small request can pin a gateway worker at 100% CPU for an extended period in graphql-limit-count routes.




This issue affects Apache APISIX: 3.17.0.



Users are recommended to upgrade to version 3.18.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/13
- https://lists.apache.org/thread/wfs7c9l8sokrh9hzv84lno12nx2zxpjk
- https://nvd.nist.gov/vuln/detail/CVE-2026-75005
