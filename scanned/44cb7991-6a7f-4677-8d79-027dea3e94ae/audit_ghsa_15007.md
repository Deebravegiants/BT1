# [H] AdGuardHome privilege escalation vulnerability

## Summary
Severity: High
Advisory: GHSA-7jp9-vgmq-c8r5
CVE: CVE-2024-36586
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-13
Source: https://github.com/advisories/GHSA-7jp9-vgmq-c8r5
Type: github-advisory

## Affected
- Go: `github.com/AdguardTeam/AdGuardHome` — affected >=0.93

## Details
An issue in AdGuardHome v0.93 to latest allows unprivileged attackers to escalate privileges via overwriting the AdGuardHome binary.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36586
- https://github.com/AdguardTeam/AdGuardHome
- https://github.com/go-compile/security-advisories/blob/master/vulns/CVE-2024-36586.md
