# [M] CVE-2026-57282

## Summary
Severity: Medium
Advisory: CVE-2026-57282
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-57282
Type: osv

## Details
Jenkins Git client Plugin 6.6.0 and earlier does not correctly escape the workspace directory name when it is embedded into a generated SSH wrapper script, allowing attackers able to control the name of a build's working directory to execute arbitrary operating system commands on the agent.

## References
- https://www.jenkins.io/security/advisory/2026-06-24/#SECURITY-3723
