# [M] Cross-site Scripting in Gogs

## Summary
Severity: Medium
Advisory: GHSA-9hx4-qm7h-x84j
CVE: CVE-2014-8683
CWE: CWE-79
Ecosystem: Go
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-9hx4-qm7h-x84j
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0.3.1 <0.5.8

## Details
Cross-site scripting (XSS) vulnerability in models/issue.go in Gogs (aka Go Git Service) 0.3.1-9 through 0.5.x before 0.5.8 allows remote attackers to inject arbitrary web script or HTML via the text parameter to api/v1/markdown.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8683
- https://github.com/gogits/gogs/commit/3abc41cccab2486012b46305827433ad6f5deade
- https://exchange.xforce.ibmcloud.com/vulnerabilities/98693
- https://github.com/gogits/gogs/releases/tag/v0.5.8
- https://gogs.io/docs/intro/change_log.html
- https://packetstormsecurity.com/files/129118/Gogs-Markdown-Renderer-Cross-Site-Scripting.html
- https://seclists.org/fulldisclosure/2014/Nov/31
- https://seclists.org/fulldisclosure/2014/Nov/34
- https://www.securityfocus.com/archive/1/533996/100/0/threaded
