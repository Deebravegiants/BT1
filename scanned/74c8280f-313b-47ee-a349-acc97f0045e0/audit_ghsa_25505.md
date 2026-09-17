# [H] Privilege escalation in beego

## Summary
Severity: High
Advisory: GHSA-ffjp-66mx-3qpj
CVE: CVE-2021-27116
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-ffjp-66mx-3qpj
Type: github-advisory

## Affected
- Go: `github.com/beego/beego/v2` — affected >=2.0.0 <2.0.2
- Go: `github.com/beego/beego` — affected >=0

## Details
An issue was discovered in file profile.go. The MemProf and GetCPUProfile functions do not correctly check whether the created file exists. As a result attackers can launch attacks symlink attacks locally. Attackers can use this vulnerability to escalate privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27116
- https://github.com/beego/beego/issues/4484
- https://github.com/beego/beego
