# [M] tiagorlampert CHAOS vulnerable to Cross Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-c5rv-hjjc-jv7m
CVE: CVE-2024-31839
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-c5rv-hjjc-jv7m
Type: github-advisory

## Affected
- Go: `github.com/tiagorlampert/CHAOS` — affected >=0

## Details
Cross Site Scripting vulnerability in tiagorlampert CHAOS v.5.0.1 allows a remote attacker to escalate privileges via the sendCommandHandler function in the handler.go component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31839
- https://blog.chebuya.com/posts/remote-code-execution-on-chaos-rat-via-spoofed-agents
- https://github.com/tiagorlampert/CHAOS
