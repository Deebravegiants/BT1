# [M] Boruta: OAuth credentials exposed in Boruta business logs

## Summary
Severity: Medium
Advisory: CVE-2026-55221
Aliases: GHSA-pqwf-v25h-4874
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-55221
Type: osv

## Details
Boruta is a standalone authorization server that aims to implement OAuth 2.0 and Openid Connect up to decentralized identity specifications. Prior to version 0.10.0, Boruta logged sensitive OAuth and OpenID Connect values in business event logs. Logged values could include access tokens, refresh tokens, authorization codes, agent tokens, direct-post codes, ID tokens, VP tokens, and tokens submitted to introspection or revocation endpoints. An attacker with access to Boruta logs, log aggregation systems, or the administration log viewer could recover these credentials and use them until expiration or revocation. This issue has been patched in version 0.10.0.

## References
- https://github.com/malach-it/boruta-server/releases/tag/0.10.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55221.json
- https://github.com/malach-it/boruta-server/security/advisories/GHSA-pqwf-v25h-4874
- https://nvd.nist.gov/vuln/detail/CVE-2026-55221
- https://github.com/malach-it/boruta-server/commit/5f8362aea39fdc2c6d6cfe41c6519985f32ba9b5
