# [M] Discourse vulnerable to private topic leak via email#send_digest

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-23546
Aliases: CVE-2022-23546, GHSA-q9jp-xv4g-328f
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-23546
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.9.0

## Details
In version 2.9.0.beta14 of Discourse, an open-source discussion platform, maliciously embedded urls can leak an admin's digest of recent topics, possibly exposing private information. A patch is available for version 2.9.0.beta15. There are no known workarounds for this issue.

## References
- https://github.com/discourse/discourse/commit/cf862e736565c6fa905c12b5dbe63d0bd056efb8
- https://github.com/discourse/discourse/security/advisories/GHSA-q9jp-xv4g-328f
- https://nvd.nist.gov/vuln/detail/CVE-2022-23546
