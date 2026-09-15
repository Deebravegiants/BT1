# [H] gardenctl is vulnerable to Command Injection when used with non‑POSIX shells

## Summary
Severity: High
Advisory: GHSA-fw33-qpx7-rhx2
CVE: CVE-2025-67508
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-11
Source: https://github.com/advisories/GHSA-fw33-qpx7-rhx2
Type: github-advisory

## Affected
- Go: `github.com/gardener/gardenctl-v2` — affected >=0 <0.0.0-20251107111549-0bdc484cb5fb

## Details
A security vulnerability was discovered in [gardenctl](https://github.com/gardener/gardenctl-v2) when it is used with non‑POSIX shells such as **[Fish](https://fishshell.com/)** and **[PowerShell](https://learn.microsoft.com/en-us/powershell/)**. Such setup could allow an attacker with administrative privileges for a Gardener project to craft malicious credential values in infrastructure Secret objects that break out of the intended string context when evaluated in Fish or PowerShell environments used by the Gardener service operators, leading to arbitrary command execution on the operator's device.

**Am I vulnerable?**
This CVE affects all Gardener operators who use  **gardenctl < v2.12.0** with non‑POSIX shells such as **[Fish](https://fishshell.com/)** and **[PowerShell](https://learn.microsoft.com/en-us/powershell/)**.

## References
- https://github.com/gardener/gardenctl-v2/security/advisories/GHSA-fw33-qpx7-rhx2
- https://nvd.nist.gov/vuln/detail/CVE-2025-67508
- https://github.com/gardener/gardenctl-v2
- https://pkg.go.dev/vuln/GO-2025-4232
