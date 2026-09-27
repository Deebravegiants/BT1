# [M] OpenClaw < 2026.4.8 - Privilege Escalation via Gateway Plugin HTTP Authentication

## Summary
Severity: Medium
Advisory: CVE-2026-42429
Aliases: GHSA-4f8g-77mw-3rxc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-42429
Type: osv

## Details
OpenClaw before 2026.4.8 contains a privilege escalation vulnerability in the gateway plugin HTTP authentication mechanism that escalates identity-bearing operator.read requests to runtime operator.write permissions. Attackers can exploit this by sending read-scoped requests through the gateway auth route to gain unauthorized write access to runtime operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42429.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4f8g-77mw-3rxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42429
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-gateway-plugin-http-authentication
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
