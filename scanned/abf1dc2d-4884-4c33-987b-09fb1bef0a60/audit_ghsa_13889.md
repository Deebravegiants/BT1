# [C] Privilege escalation in MOSN

## Summary
Severity: Critical
Advisory: GHSA-5vx9-j5cw-47vq
CVE: CVE-2021-32163
CWE: CWE-178, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-17
Source: https://github.com/advisories/GHSA-5vx9-j5cw-47vq
Type: github-advisory

## Affected
- Go: `mosn.io/mosn` — affected >=0 <0.23.0

## Details
Authentication vulnerability in MOSN before v.0.23.0 allows attacker to escalate privileges via case-sensitive JWT authorization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32163
- https://github.com/mosn/mosn/issues/1633
- https://github.com/mosn/mosn/pull/1637
- https://github.com/mosn/mosn
