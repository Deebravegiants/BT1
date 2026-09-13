# [H] Apache APISIX: attach-consumer-label does not strip client-supplied consumer-label headers

## Summary
Severity: High
Advisory: BIT-apisix-2026-63041
Aliases: CVE-2026-63041
Ecosystem: Bitnami
Published: 2026-08-28
Source: https://osv.dev/vulnerability/BIT-apisix-2026-63041
Type: osv

## Affected
- Bitnami: `apisix` — affected >=3.11.0 <3.18.0

## Details
Reliance on Untrusted Inputs in a Security Decision vulnerability in Apache APISIX.

This vulnerability allows an attacker to escalate privilege or perform an authorization bypass by sending certain values that the attach-consumer-label plugin does not sanitise correctly.


This issue affects Apache APISIX: from 3.11.0 through 3.17.0.



Users are recommended to upgrade to version 3.18.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/11
- https://lists.apache.org/thread/yg9tgn699rz7kyglw82m1775do8frjr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-63041
