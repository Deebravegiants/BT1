# [H] Discourse vulnerable to ossible DDoS due to unbounded limits in various controller actions

## Summary
Severity: High
Advisory: BIT-discourse-2023-38684
Aliases: CVE-2023-38684, GHSA-ff7g-xv79-hgmf
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-38684
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.6

## Details
Discourse is an open source discussion platform. Prior to version 3.0.6 of the `stable` branch and version 3.1.0.beta7 of the `beta` and `tests-passed` branches, in multiple controller actions, Discourse accepts limit params but does not impose any upper bound on the values being accepted. Without an upper bound, the software may allow arbitrary users to generate DB queries which may end up exhausting the resources on the server. The issue is patched in version 3.0.6 of the `stable` branch and version 3.1.0.beta7 of the `beta` and `tests-passed` branches. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/commit/bfc3132bb22bd5b7e86f428746b89c4d3d7f5a70
- https://github.com/discourse/discourse/security/advisories/GHSA-ff7g-xv79-hgmf
- https://nvd.nist.gov/vuln/detail/CVE-2023-38684
