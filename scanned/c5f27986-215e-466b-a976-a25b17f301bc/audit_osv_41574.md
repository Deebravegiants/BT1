# [M] OpenClaw < 2026.5.27 Token Leakage via MS Teams Outbound Requests

## Summary
Severity: Medium
Advisory: CVE-2026-62213
Aliases: GHSA-v54h-q2vx-vgg4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62213
Type: osv

## Details
OpenClaw versions before 2026.5.27 contain a token leakage vulnerability in MS Teams outbound requests that allows lower-trust callers to expose Bot Framework tokens. Attackers can access configured input paths to retrieve credentials that should remain within the trusted boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62213.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v54h-q2vx-vgg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-62213
- https://www.vulncheck.com/advisories/openclaw-token-leakage-via-ms-teams-outbound-requests
- https://github.com/openclaw/openclaw
