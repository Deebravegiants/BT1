# [M] BIT-discourse-2022-23548

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-23548
Aliases: CVE-2022-23548, GHSA-7rw2-f4x7-7pxf
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-23548
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.14

## Details
Discourse is an option source discussion platform. Prior to version 2.8.14 on the `stable` branch, parsing posts can be susceptible to regular expression denial of service (ReDoS) attacks. This issue is patched in version 2.8.14. There are no known workarounds.

## References
- https://github.com/discourse/discourse/pull/19737
- https://github.com/discourse/discourse/security/advisories/GHSA-7rw2-f4x7-7pxf
- https://nvd.nist.gov/vuln/detail/CVE-2022-23548
