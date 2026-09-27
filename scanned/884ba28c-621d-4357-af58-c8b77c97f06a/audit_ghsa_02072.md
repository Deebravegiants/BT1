# [M] SQL Injection in gogs.io/gogs

## Summary
Severity: Medium
Advisory: GHSA-mr6h-chqp-p9g2
CVE: CVE-2014-8681
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-mr6h-chqp-p9g2
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0.3.1 <0.5.8
- Go: `github.com/gogits/gogs` — affected >=0.3.1 <0.5.8

## Details
SQL injection vulnerability in the GetIssues function in models/issue.go in Gogs (aka Go Git Service) 0.3.1-9 through 0.5.6.x before 0.5.6.1025 Beta allows remote attackers to execute arbitrary SQL commands via the label parameter to user/repos/issues.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8681
- https://github.com/gogits/gogs/commit/83283bca4cb4e0f4ec48a28af680f0d88db3d2c8
- https://github.com/gogs/gogs/commit/83283bca4cb4e0f4ec48a28af680f0d88db3d2c8
- https://exchange.xforce.ibmcloud.com/vulnerabilities/98695
- https://github.com/gogits/gogs
- https://github.com/gogits/gogs/releases/tag/v0.5.8
- https://pkg.go.dev/vuln/GO-2020-0021
- https://seclists.org/fulldisclosure/2014/Nov/31
- https://web.archive.org/web/20150711111508/http://gogs.io/docs/intro/change_log.html#v0.5.8-%40-2014-11-19
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-8681
- https://www.exploit-db.com/exploits/35237
- http://packetstormsecurity.com/files/129116/Gogs-Label-Search-Blind-SQL-Injection.html
- http://seclists.org/fulldisclosure/2014/Nov/31
