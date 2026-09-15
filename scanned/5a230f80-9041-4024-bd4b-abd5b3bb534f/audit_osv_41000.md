# [H] 9router: Image prefetch DNS rebinding allows SSRF to internal services

## Summary
Severity: High
Advisory: CVE-2026-56676
Aliases: GHSA-cmhj-wh2f-9cgx
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-56676
Type: osv

## Details
9Router is an AI router & token saver. Prior to 0.5.2, 9router validates image URLs by resolving the host before fetching, but open-sse/translator/concerns/image.js performs the later server-side image fetch with a separate DNS resolution. An authenticated attacker with access to the LLM proxy can use a vision-capable model and an attacker-controlled DNS name that first resolves to a public IP and then rebinds to an internal address, allowing server-side requests to internal-only HTTP services. This issue is fixed in version 0.5.2.

## References
- https://github.com/decolua/9router/releases/tag/v0.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56676.json
- https://github.com/decolua/9router/security/advisories/GHSA-cmhj-wh2f-9cgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-56676
- https://github.com/decolua/9router/commit/c7d07448c58bec1200741de0b73305b860416b82
