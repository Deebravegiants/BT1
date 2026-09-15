# [H] Apache Ambari: Remote Code Injection in Ambari Metrics and AMS Alerts

## Summary
Severity: High
Advisory: CVE-2024-51941
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-51941
Type: osv

## Details
A remote code injection vulnerability exists in the Ambari Metrics and 
AMS Alerts feature, allowing authenticated users to inject and execute 
arbitrary code. The vulnerability occurs when processing alert 
definitions, where malicious input can be injected into the alert script
 execution path. An attacker with authenticated access can exploit this 
vulnerability to execute arbitrary commands on the server. The issue has
 been fixed in the latest versions of Ambari.

## References
- http://www.openwall.com/lists/oss-security/2025/01/21/9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51941.json
- https://lists.apache.org/thread/xq50nlff7o7z1kq3y637clzzl6mjhl8j
- https://nvd.nist.gov/vuln/detail/CVE-2024-51941
