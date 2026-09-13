# [M] Apache Kylin: SSRF vulnerability in the diagnosis api

## Summary
Severity: Medium
Advisory: CVE-2024-48944
Aliases: GHSA-3v67-545x-ffc3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2024-48944
Type: osv

## Details
Server-Side Request Forgery (SSRF) vulnerability in Apache Kylin. Through a kylin server, an attacker may forge a request to invoke "/kylin/api/xxx/diag" api on another internal host and possibly get leaked information. There are two preconditions: 1) The attacker has got admin access to a kylin server; 2) Another internal host has the "/kylin/api/xxx/diag" api

endpoint open for service.


This issue affects Apache Kylin: from 5.0.0 
through 

5.0.1.

Users are recommended to upgrade to version 5.0.2, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/03/27/5
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48944.json
- https://lists.apache.org/thread/1xxxtdfh9hzqsqgb1pd9grb8hvqdyc9x
- https://nvd.nist.gov/vuln/detail/CVE-2024-48944
