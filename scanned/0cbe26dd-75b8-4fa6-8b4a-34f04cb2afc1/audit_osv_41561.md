# [C] OpenClaw 2026.5.20 < 2026.6.9 Privilege Escalation via Plugin Install

## Summary
Severity: Critical
Advisory: CVE-2026-62194
Aliases: GHSA-7vrr-rp4x-4g76
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62194
Type: osv

## Details
OpenClaw versions 2026.5.20 before 2026.6.9 contain a privilege escalation vulnerability in plugin install commands that allows lower-trust callers to execute or persist actions beyond their intended authorization. Attackers can exploit misconfigured input paths or enabled features to escalate privileges and perform unauthorized actions when the feature is reachable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62194.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7vrr-rp4x-4g76
- https://nvd.nist.gov/vuln/detail/CVE-2026-62194
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-plugin-install
- https://github.com/openclaw/openclaw
