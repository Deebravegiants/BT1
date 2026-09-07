# [H] SQL Injection in Gogs

## Summary
Severity: High
Advisory: GHSA-g6xv-8q23-w2q3
CVE: CVE-2014-8682
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-g6xv-8q23-w2q3
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0.3.1 <0.5.8

## Details
Multiple SQL injection vulnerabilities in Gogs (aka Go Git Service) 0.3.1-9 through 0.5.x before 0.5.6.1105 Beta allow remote attackers to execute arbitrary SQL commands via the q parameter to (1) api/v1/repos/search, which is not properly handled in models/repo.go, or (2) api/v1/users/search, which is not properly handled in models/user.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8682
- https://github.com/gogits/gogs/commit/0c5ba4573aecc9eaed669e9431a70a5d9f184b8d
- https://exchange.xforce.ibmcloud.com/vulnerabilities/98694
- https://github.com/gogits/gogs/releases/tag/v0.5.8
- https://www.exploit-db.com/exploits/35238
- http://gogs.io/docs/intro/change_log.html
- http://packetstormsecurity.com/files/129116/Gogs-Label-Search-Blind-SQL-Injection.html
- http://packetstormsecurity.com/files/129117/Gogs-Repository-Search-SQL-Injection.html
- http://seclists.org/fulldisclosure/2014/Nov/31
- http://seclists.org/fulldisclosure/2014/Nov/33
- http://www.exploit-db.com/exploits/35238
- http://www.securityfocus.com/archive/1/533995/100/0/threaded
- http://www.securityfocus.com/bid/71187
