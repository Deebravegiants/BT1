# [H] Apache APISIX: authz-casdoor incorrect session sharing

## Summary
Severity: High
Advisory: BIT-apisix-2026-47339
Aliases: CVE-2026-47339
Ecosystem: Bitnami
Published: 2026-06-23
Source: https://osv.dev/vulnerability/BIT-apisix-2026-47339
Type: osv

## Affected
- Bitnami: `apisix` — affected >=2.14.1 <3.17.0

## Details
Incorrect Authorization vulnerability in Apache APISIX.

An attacker can capitalise on authz-casdoor plugin under default configuration to authenticate themselves with credentials from a different source.
This issue affects Apache APISIX: from 2.14.1 through 3.16.0.

Users are recommended to upgrade to version 3.17.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/19/9
- https://lists.apache.org/thread/lk4q5o855cocc7zq5wh1zlctfmcq6f76
- https://nvd.nist.gov/vuln/detail/CVE-2026-47339
