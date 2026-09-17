# [H] Kolide Agent Privilege Escalation (Windows, Versions >= 1.5.3, < 1.12.3)

## Summary
Severity: High
Advisory: GHSA-66q9-2rvx-qfj5
CVE: CVE-2024-54131
CWE: CWE-276, CWE-456
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-66q9-2rvx-qfj5
Type: github-advisory

## Affected
- Go: `github.com/kolide/launcher` — affected >=1.5.3 <1.12.3

## Details
An implementation bug in the Kolide Agent (known as `launcher`) allows for local privilege escalation to the SYSTEM user on Windows 10 and 11. Impacted versions include versions >= 1.5.3 and the fix has been released in 1.12.3. 

The bug was introduced in version 1.5.3 when launcher started storing upgraded binaries in the ProgramData directory (#1510). This move to the new directory meant the launcher root directory inherited default permissions that are not as strict as the previous location. These incorrect default permissions in conjunction with an omitted SystemDrive environmental variable (when launcher starts osqueryd), allows a malicious actor with access to the local Windows device to successfully place an arbitrary DLL into the osqueryd process's search path. Under some circumstances, this DLL will be executed when osqueryd performs a WMI query. This combination of events could then allow the attacker to escalate their privileges to SYSTEM.

This issue was found by Bryan Alexander of Atredis Partners and responsibly reported through the Kolide bug bounty program. Kolide made the appropriate changes and released a fix in version 1.12.3 of the `launcher` package.

## References
- https://github.com/kolide/launcher/security/advisories/GHSA-66q9-2rvx-qfj5
- https://github.com/kolide/launcher/pull/1510
- https://github.com/kolide/launcher
