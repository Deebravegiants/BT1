# [C] Fleet vulnerable to OS command injection via crafted software package metadata in uninstall scripts

## Summary
Severity: Critical
Advisory: CVE-2026-34387
Aliases: GHSA-7rhw-5mpv-gp4h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-34387
Type: osv

## Details
Fleet is open source device management software. Prior to 4.81.1, a command injection vulnerability in Fleet's software installer pipeline allows an attacker to achieve arbitrary code execution as root (macOS/Linux) or SYSTEM (Windows) on managed hosts when an uninstall is triggered for a crafted software package. Version 4.81.1 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34387.json
- https://github.com/fleetdm/fleet/security/advisories/GHSA-7rhw-5mpv-gp4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34387
