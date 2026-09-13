# [H] When running Apache Tomcat on Windows with HTTP PUTs enabled it was possible to upload a JSP file to the server

## Summary
Severity: High
Advisory: GHSA-pjfr-qf3p-3q25
CVE: CVE-2017-12615
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-pjfr-qf3p-3q25
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=7.0.0 <7.0.79

## Details
When running Apache Tomcat 7.0.0 to 7.0.79 on Windows with HTTP PUTs enabled (e.g. via setting the readonly initialisation parameter of the Default to false) it was possible to upload a JSP file to the server via a specially crafted request. This JSP could then be requested and any code it contained would be executed by the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12615
- https://www.synology.com/support/security/Synology_SA_17_54_Tomcat
- https://www.exploit-db.com/exploits/42953
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2017-12615
- https://security.netapp.com/advisory/ntap-20171018-0001
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r9136ff5b13e4f1941360b5a309efee2c114a14855578c3a2cbe5d19c%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r6d03e45b81eab03580cf7f8bb51cb3e9a1b10a2cc0c6a2d3cc92ed0c@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r6d03e45b81eab03580cf7f8bb51cb3e9a1b10a2cc0c6a2d3cc92ed0c%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/8fcb1e2d5895413abcf266f011b9918ae03e0b7daceb118ffbf23f8c@%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/8fcb1e2d5895413abcf266f011b9918ae03e0b7daceb118ffbf23f8c%40%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/845312a10aabbe2c499fca94003881d2c79fc993d85f34c1f5c77424@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/845312a10aabbe2c499fca94003881d2c79fc993d85f34c1f5c77424%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/3d19773b4cf0377db62d1e9328bf9160bf1819f04f988315086931d7@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/3d19773b4cf0377db62d1e9328bf9160bf1819f04f988315086931d7%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/388a323769f1dff84c9ec905455aa73fbcb20338e3c7eb131457f708@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/388a323769f1dff84c9ec905455aa73fbcb20338e3c7eb131457f708%40%3Cdev.tomcat.apache.org%3E
- https://github.com/breaktoprotect/CVE-2017-12615
- https://github.com/advisories/GHSA-pjfr-qf3p-3q25
- https://access.redhat.com/errata/RHSA-2018:0466
