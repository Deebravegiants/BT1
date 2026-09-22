# [C] nGrinder vulnerable to unsafe Java objects deserialization

## Summary
Severity: Critical
Advisory: GHSA-j7jm-8gf5-frcm
CVE: CVE-2024-28213
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-07
Source: https://github.com/advisories/GHSA-j7jm-8gf5-frcm
Type: github-advisory

## Affected
- Maven: `org.ngrinder:ngrinder-core` — affected >=0 <3.5.9

## Details
nGrinder before 3.5.9 allows to accept serialized Java objects from unauthenticated users, which could allow remote attacker to execute arbitrary code via unsafe Java objects deserialization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28213
- https://github.com/naver/ngrinder/commit/85efa4a075354e077a700262ef78e2e9119881bf
- https://cve.naver.com/detail/cve-2024-28213.html
- https://github.com/naver/ngrinder
