# [M] OpenClaw 2026.6.5 < 2026.6.9 Authentication Bypass via Plugin Install

## Summary
Severity: Medium
Advisory: CVE-2026-62193
Aliases: GHSA-wgq8-x5wm-g4rw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62193
Type: osv

## Details
OpenClaw versions 2026.6.5 before 2026.6.9 contain a vulnerability in the plugin install wrappers that could skip the install policy (authorization) check. When the affected feature is enabled and reachable, a lower-trust caller or a configured input path could execute or persist actions beyond the caller's intended authorization. Impact depends on the operator's configuration and whether lower-trust input can reach the affected path. The issue is fixed in 2026.6.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62193.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wgq8-x5wm-g4rw
- https://nvd.nist.gov/vuln/detail/CVE-2026-62193
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-via-plugin-install
- https://github.com/openclaw/openclaw
