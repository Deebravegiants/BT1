# [M] Pi-hole has a Local Privilege Escalation (post-compromise, pihole -> root).

## Summary
Severity: Medium
Advisory: CVE-2026-33727
Aliases: GHSA-c935-8g63-qp74
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-33727
Type: osv

## Details
Pi-hole is a Linux network-level advertisement and Internet tracker blocking application. Version 6.4 has a local privilege-escalation vulnerability allows code execution as root from the low-privilege pihole account. Important context: the pihole account uses nologin, so this is not a direct interactive-login issue. However, nologin does not prevent code from running as UID pihole if a Pi-hole component is compromised. In that realistic post-compromise scenario, attacker-controlled content in /etc/pihole/versions is sourced by root-run Pi-hole scripts, leading to root code execution. This vulnerability is fixed in 6.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33727.json
- https://github.com/pi-hole/pi-hole/security/advisories/GHSA-c935-8g63-qp74
- https://nvd.nist.gov/vuln/detail/CVE-2026-33727
