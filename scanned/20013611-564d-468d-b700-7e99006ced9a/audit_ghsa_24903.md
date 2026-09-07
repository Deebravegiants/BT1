# [H] Improper Authorization in Undertoe

## Summary
Severity: High
Advisory: GHSA-gv2w-88hx-8m9r
CVE: CVE-2020-1745
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gv2w-88hx-8m9r
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.0.30

## Details
A file inclusion vulnerability was found in the AJP connector enabled with a default AJP configuration port of 8009 in Undertow version 2.0.29.Final and before and was fixed in 2.0.30.Final. A remote, unauthenticated attacker could exploit this vulnerability to read web application files from a vulnerable server. In instances where the vulnerable server allows file uploads, an attacker could upload malicious JavaServer Pages (JSP) code within a variety of file types and trigger this vulnerability to gain remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1745
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1745
- https://meterpreter.org/cve-2020-1938-apache-tomcat-ajp-connector-remote-code-execution-vulnerability-alert
- https://www.cnvd.org.cn/webinfo/show/5415
- https://www.tenable.com/blog/cve-2020-1938-ghostcat-apache-tomcat-ajp-file-readinclusion-vulnerability-cnvd-2020-10487
