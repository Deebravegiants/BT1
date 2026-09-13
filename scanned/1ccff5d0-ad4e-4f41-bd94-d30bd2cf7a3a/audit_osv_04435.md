# [M] Discourse vulnerable to Server-Side Request Forgery via FastImage

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-37157
Aliases: CVE-2024-37157, GHSA-46pq-7958-fc68
Ecosystem: Bitnami
Published: 2024-07-09
Source: https://osv.dev/vulnerability/BIT-discourse-2024-37157
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.3

## Details
Discourse is an open-source discussion platform. Prior to version 3.2.3 on the `stable` branch and version 3.3.0.beta4 on the `beta` and `tests-passed` branches, a malicious actor could get the FastImage library to redirect requests to an internal Discourse IP. This issue is patched in version 3.2.3 on the `stable` branch and version 3.3.0.beta4 on the `beta` and `tests-passed` branches. No known workarounds are available.

## References
- https://github.com/discourse/discourse/commit/5b8cf11b69e05d5c058c1148ec69ec309491fa6e
- https://github.com/discourse/discourse/commit/67e78086035cec494b15ce79342a0cb9052c2d95
- https://github.com/discourse/discourse/security/advisories/GHSA-46pq-7958-fc68
- https://nvd.nist.gov/vuln/detail/CVE-2024-37157
