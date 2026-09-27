# [C] CVE-2024-51378

## Summary
Severity: Critical
Advisory: CVE-2024-51378
CVSS: 10.0 (CVSS:3.1/AC:L/AV:N/A:H/C:H/I:H/PR:N/S:C/UI:N)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-51378
Type: osv

## Details
getresetstatus in dns/views.py and ftp/views.py in CyberPanel (aka Cyber Panel) before 1c0c6cb allows remote attackers to bypass authentication and execute arbitrary commands via /dns/getresetstatus or /ftp/getresetstatus by bypassing secMiddleware (which is only for a POST request) and using shell metacharacters in the statusfile property, as exploited in the wild in October 2024 by PSAUX. Versions through 2.3.6 and (unpatched) 2.3.7 are affected.

## References
- https://cwe.mitre.org/data/definitions/420.html
- https://cwe.mitre.org/data/definitions/78.html
- https://cyberpanel.net/KnowledgeBase/home/change-logs/
- https://refr4g.github.io/posts/cyberpanel-command-injection-vulnerability/
- https://www.bleepingcomputer.com/news/security/massive-psaux-ransomware-attack-targets-22-000-cyberpanel-instances/
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-51378
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51378.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-51378
- https://github.com/usmannasir/cyberpanel/commit/1c0c6cbcf71abe573da0b5fddfb9603e7477f683
- https://cyberpanel.net/blog/detials-and-fix-of-recent-security-issue-and-patch-of-cyberpanel
