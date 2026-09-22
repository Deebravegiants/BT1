# [M] Malicious users in Discourse can create spam topics as any user due to improper access control

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-23615
Aliases: CVE-2023-23615, GHSA-7mf3-5v84-wxq8
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-23615
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.1

## Details
Discourse is an open source discussion platform. The embeddable comments can be exploited to create new topics as any user but without any clear title or content. This issue is patched in the latest stable, beta and tests-passed versions of Discourse. As a workaround, disable embeddable comments by deleting all embeddable hosts.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-7mf3-5v84-wxq8
- https://nvd.nist.gov/vuln/detail/CVE-2023-23615
