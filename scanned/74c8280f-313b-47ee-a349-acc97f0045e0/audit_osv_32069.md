# [H] Apache Ambari: XML External Entity (XXE) Vulnerability in Ambari/Oozie

## Summary
Severity: High
Advisory: CVE-2025-23195
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2025-23195
Type: osv

## Details
An XML External Entity (XXE) vulnerability exists in the Ambari/Oozie 
project, allowing an attacker to inject malicious XML entities. This 
vulnerability occurs due to insecure parsing of XML input using the 
`DocumentBuilderFactory` class without disabling external entity 
resolution. An attacker can exploit this vulnerability to read arbitrary
 files on the server or perform server-side request forgery (SSRF) 
attacks. The issue has been fixed in both Ambari 2.7.9 and the trunk 
branch.

## References
- http://www.openwall.com/lists/oss-security/2025/01/21/7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23195.json
- https://lists.apache.org/thread/hsb6mvxd7g37dq1ygtd0pd88gs9tfcwq
- https://nvd.nist.gov/vuln/detail/CVE-2025-23195
