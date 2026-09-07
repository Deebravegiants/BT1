# [C] Apache Struts vulnerable to path traversal

## Summary
Severity: Critical
Advisory: GHSA-2j39-qcjm-428w
CVE: CVE-2023-50164
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-07
Source: https://github.com/advisories/GHSA-2j39-qcjm-428w
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.5.33
- Maven: `org.apache.struts:struts2-core` — affected >=6.0.0 <6.3.0.2

## Details
An attacker can manipulate file upload params to enable paths traversal and under some circumstances this can lead to uploading a malicious file which can be used to perform Remote Code Execution.
Users are recommended to upgrade to versions Struts 2.5.33 or Struts 6.3.0.2 or greater to fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50164
- https://github.com/apache/struts/commit/162e29fee9136f4bfd9b2376da2cbf590f9ea163
- https://github.com/apache/struts/commit/d8c69691ef1d15e76a5f4fcf33039316da2340b6
- https://cwiki.apache.org/confluence/display/WW/S2-066
- https://github.com/apache/struts
- https://lists.apache.org/thread/yh09b3fkf6vz5d6jdgrlvmg60lfwtqhj
- https://security.netapp.com/advisory/ntap-20231214-0010
- https://www.openwall.com/lists/oss-security/2023/12/07/1
- http://packetstormsecurity.com/files/176157/Struts-S2-066-File-Upload-Remote-Code-Execution.html
- http://www.openwall.com/lists/oss-security/2023/12/07/1
