# [H] Discourse vulnerable to DoS through Onebox

## Summary
Severity: High
Advisory: BIT-discourse-2024-35227
Aliases: CVE-2024-35227, GHSA-664f-xwjw-752c
Ecosystem: Bitnami
Published: 2024-07-09
Source: https://osv.dev/vulnerability/BIT-discourse-2024-35227
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.3

## Details
Discourse is an open-source discussion platform. Prior to version 3.2.3 on the `stable` branch and version 3.3.0.beta3 on the `tests-passed` branch, Oneboxing against a carefully crafted malicious URL can reduce the availability of a Discourse instance. The problem has been patched in version 3.2.3 on the `stable` branch and version 3.3.0.beta3 on the `tests-passed` branch. There are no known workarounds available for this vulnerability.

## References
- https://github.com/discourse/discourse/commit/10afe5fcf1ebf2e49cb80716d5e62e184c53519b
- https://github.com/discourse/discourse/commit/6ce5673d2c1a511b602e1b2ade6cdc898d14ab36
- https://github.com/discourse/discourse/security/advisories/GHSA-664f-xwjw-752c
- https://nvd.nist.gov/vuln/detail/CVE-2024-35227
