# [M] Discourse vulnerable to Allocation of Resources Without Limits via Chat drafts

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-22740
Aliases: CVE-2023-22740, GHSA-pwj4-rf62-p224
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-22740
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.1

## Details
Discourse is an open source platform for community discussion. Versions prior to 3.1.0.beta1 (beta) (tests-passed) are vulnerable to  Allocation of Resources Without Limits. Users can create chat drafts of an unlimited length, which can cause a denial of service by generating an excessive load on the server. Additionally, an unlimited number of drafts were loaded when loading the user. This issue has been patched in version 2.1.0.beta1 (beta) and (tests-passed). Users should upgrade to the latest version where a limit has been introduced. There are no workarounds available.

## References
- https://github.com/discourse/discourse/commit/5eaf0802398ff06604f03b27a28dd274f2ffa576
- https://github.com/discourse/discourse/security/advisories/GHSA-pwj4-rf62-p224
- https://nvd.nist.gov/vuln/detail/CVE-2023-22740
