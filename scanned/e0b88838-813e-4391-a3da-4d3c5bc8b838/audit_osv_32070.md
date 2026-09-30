# [H] Apache Ambari: Code Injection Vulnerability in Ambari Alert Definition

## Summary
Severity: High
Advisory: CVE-2025-23196
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2025-23196
Type: osv

## Details
A code injection vulnerability exists in the Ambari Alert Definition 
feature, allowing authenticated users to inject and execute arbitrary 
shell commands. The vulnerability arises when defining alert scripts, 
where the script filename field is executed using `sh -c`. An attacker 
with authenticated access can exploit this vulnerability to inject 
malicious commands, leading to remote code execution on the server. The 
issue has been fixed in the latest versions of Ambari.

## References
- http://www.openwall.com/lists/oss-security/2025/01/21/8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23196.json
- https://lists.apache.org/thread/70g1l5lxvko7kvhyxmtmklhhfrlon837
- https://nvd.nist.gov/vuln/detail/CVE-2025-23196
