# [H] Code injection in ansible semaphore

## Summary
Severity: High
Advisory: GHSA-3r32-cp7v-5wq4
CVE: CVE-2023-39059
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-3r32-cp7v-5wq4
Type: github-advisory

## Affected
- Go: `github.com/ansible-semaphore/semaphore` — affected >=0

## Details
An issue in ansible semaphore v.2.8.90 allows a remote attacker to execute arbitrary code via a crafted payload to the extra variables parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39059
- https://gist.github.com/Alevsk/1757da24c5fb8db735d392fd4146ca3a
- https://github.com/ansible-semaphore/semaphore
- https://www.alevsk.com/2023/07/a-quick-story-of-security-pitfalls-with-execcommand-in-software-integrations
