# [C] Bitwarden Server < 2026.4.0 Missing Authorization via Provider Clients

## Summary
Severity: Critical
Advisory: CVE-2026-43639
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43639
Type: osv

## Details
Bitwarden Server prior to v2026.4.0 contains a missing authorization vulnerability that allows a provider service user to add an arbitrary organization to their provider via `POST /providers/{providerId}/clients/existing`, resulting in takeover of the target organization; self-hosted installations are unaffected as this endpoint is restricted to Cloud via SelfHosted(NotSelfHostedOnly = true).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43639.json
- https://github.com/bitwarden/server/releases/tag/v2026.4.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-43639
- https://www.vulncheck.com/advisories/bitwarden-server-missing-authorization-via-provider-clients
- https://github.com/bitwarden/server/pull/7372
- https://github.com/bitwarden/server/commit/0918bfdda6f5eec391c69bd9074f6aef4eac0b1d
- https://github.com/bitwarden/server
- https://sanjokkarki.com.np/blog/bitwarden-provider-takeover
