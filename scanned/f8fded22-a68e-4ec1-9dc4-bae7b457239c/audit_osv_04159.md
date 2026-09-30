# [H] Apache APISIX: Improper authentication in cas-auth plugin

## Summary
Severity: High
Advisory: BIT-apisix-2026-49872
Aliases: CVE-2026-49872
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-apisix-2026-49872
Type: osv

## Affected
- Bitnami: `apisix` — affected >=3.0.0 <3.17.0

## Details
Improper Authentication vulnerability in Apache APISIX.

When the cas-auth plugin is used in a route, an attacker can possibly authenticate itself with credentials from a different source.
This issue affects Apache APISIX: from 3.0.0 through 3.16.0.

Users are recommended to upgrade to version 3.17.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/19/15
- https://lists.apache.org/thread/bzjpo60ygxo7kxdqf7vw3l5zw2lh6m5k
- https://nvd.nist.gov/vuln/detail/CVE-2026-49872
