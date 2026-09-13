# [M] BIT-discourse-2023-36818

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-36818
Aliases: CVE-2023-36818, GHSA-gxqx-3q2p-37gm
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-36818
Type: osv

## Affected
- Bitnami: `discourse` — affected >=3.1.0-beta5

## Details
Discourse is an open source discussion platform. In affected versions a request to create or update custom sidebar section can cause a denial of service. This issue has been patched in commit `52b003d915`. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/commit/52b003d915761f1581ae2d105f3cbe76df7bf1ff
- https://github.com/discourse/discourse/security/advisories/GHSA-gxqx-3q2p-37gm
