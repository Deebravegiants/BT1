# [H] Privilege escalation in beego

## Summary
Severity: High
Advisory: GHSA-2v6v-q994-xvxx
CVE: CVE-2021-27117
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-2v6v-q994-xvxx
Type: github-advisory

## Affected
- Go: `github.com/beego/beego/v2` — affected >=2.0.0 <2.0.2
- Go: `github.com/beego/beego` — affected >=0

## Details
beego is an open-source, high-performance web framework for the Go programming language. An issue was discovered in file profile.go in function GetCPUProfile in beego through 2.0.2, allows attackers to launch symlink attacks locally.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27117
- https://github.com/beego/beego/issues/4484
- https://github.com/beego/beego
