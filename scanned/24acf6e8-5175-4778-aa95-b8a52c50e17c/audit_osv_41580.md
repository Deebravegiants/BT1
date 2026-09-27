# [C] OpenClaw < 2026.5.18 Authorization Bypass via Device-pair

## Summary
Severity: Critical
Advisory: CVE-2026-62223
Aliases: GHSA-hx85-fgcw-9vrc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62223
Type: osv

## Details
OpenClaw before 2026.5.18 contain an authorization bypass vulnerability in the device-pair approval feature that allows lower-trust callers to execute actions beyond their intended authorization. Attackers can exploit misconfigured input paths to execute or persist unauthorized actions when the affected feature is enabled and reachable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62223.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hx85-fgcw-9vrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-62223
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-device-pair
- https://github.com/openclaw/openclaw
