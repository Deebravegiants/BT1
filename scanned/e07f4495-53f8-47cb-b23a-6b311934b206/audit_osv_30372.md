# [C] CVE-2024-51567

## Summary
Severity: Critical
Advisory: CVE-2024-51567
CVSS: 10.0 (CVSS:3.1/AC:L/AV:N/A:H/C:H/I:H/PR:N/S:C/UI:N)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-51567
Type: osv

## Details
upgrademysqlstatus in databases/views.py in CyberPanel (aka Cyber Panel) before 5b08cd6 allows remote attackers to bypass authentication and execute arbitrary commands via /dataBases/upgrademysqlstatus by bypassing secMiddleware (which is only for a POST request) and using shell metacharacters in the statusfile property, as exploited in the wild in October 2024 by PSAUX. Versions through 2.3.6 and (unpatched) 2.3.7 are affected.

## References
- https://cwe.mitre.org/data/definitions/420.html
- https://cwe.mitre.org/data/definitions/78.html
- https://cyberpanel.net/KnowledgeBase/home/change-logs/
- https://dreyand.rs/code/review/2024/10/27/what-are-my-options-cyberpanel-v236-pre-auth-rce
- https://www.bleepingcomputer.com/news/security/massive-psaux-ransomware-attack-targets-22-000-cyberpanel-instances/
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-51567
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51567.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-51567
- https://github.com/usmannasir/cyberpanel/commit/5b08cd6d53f4dbc2107ad9f555122ce8b0996515
- https://cyberpanel.net/blog/detials-and-fix-of-recent-security-issue-and-patch-of-cyberpanel
