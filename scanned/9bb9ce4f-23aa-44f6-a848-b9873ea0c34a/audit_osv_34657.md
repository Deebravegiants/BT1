# [C] CVE-2025-63414

## Summary
Severity: Critical
Advisory: CVE-2025-63414
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-63414
Type: osv

## Details
A Path Traversal vulnerability in the Allsky WebUI version v2024.12.06_06 allows an unauthenticated remote attacker to achieve arbitrary command execution. By sending a crafted HTTP request to the /html/execute.php endpoint with a malicious payload in the id parameter, an attacker can execute arbitrary commands on the underlying operating system, leading to full remote code execution (RCE).

## References
- https://gh0stmezh.wordpress.com/2025/12/02/cve-2025-63414/
- https://github.com/AllskyTeam/allsky/blob/master/html/execute.php
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63414.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63414
- https://github.com/AllskyTeam/allsky
