# [C] Apache APISIX: forward auth plugin allows header injection

## Summary
Severity: Critical
Advisory: BIT-apisix-2026-31908
Aliases: CVE-2026-31908
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-apisix-2026-31908
Type: osv

## Affected
- Bitnami: `apisix` — affected >=2.12.0 <3.16.0

## Details
Header injection vulnerability in Apache APISIX.

The attacker can take advantage of certain configuration in forward-auth plugin to inject malicious headers.
This issue affects Apache APISIX: from 2.12.0 through 3.15.0.

Users are recommended to upgrade to version 3.16.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/04/14/3
- https://lists.apache.org/thread/sob643s5lztov7x579j8o0c444t36n6b
- https://nvd.nist.gov/vuln/detail/CVE-2026-31908
