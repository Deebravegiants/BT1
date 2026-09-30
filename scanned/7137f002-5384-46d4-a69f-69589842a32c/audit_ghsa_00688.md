# [C] Improper Privilege Management in Tomcat

## Summary
Severity: Critical
Advisory: GHSA-c9hw-wf7x-jp9j
CVE: CVE-2020-1938
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-c9hw-wf7x-jp9j
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0 <9.0.31
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.0.0 <8.5.51
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=7.0.0 <7.0.100

## Details
When using the Apache JServ Protocol (AJP), care must be taken when trusting incoming connections to Apache Tomcat. Tomcat treats AJP connections as having higher trust than, for example, a similar HTTP connection. If such connections are available to an attacker, they can be exploited in ways that may be surprising. In Apache Tomcat 9.0.0.M1 to 9.0.0.30, 8.5.0 to 8.5.50 and 7.0.0 to 7.0.99, Tomcat shipped with an AJP Connector enabled by default that listened on all configured IP addresses. It was expected (and recommended in the security guide) that this Connector would be disabled if not required. This vulnerability report identified a mechanism that allowed: returning arbitrary files from anywhere in the web application, processing any file in the web application as a JSP Further, if the web application allowed file upload and stored those files within the web application (or the attacker was able to control the content of the web application by some other means) then this, along with the ability to process a file as a JSP, made remote code execution possible. It is important to note that mitigation is only required if an AJP port is accessible to untrusted users. Users wishing to take a defence-in-depth approach and block the vector that permits returning arbitrary files and execution as JSP may upgrade to Apache Tomcat 9.0.31, 8.5.51 or 7.0.100 or later. A number of changes were made to the default AJP Connector configuration in 9.0.31 to harden the default configuration. It is likely that users upgrading to 9.0.31, 8.5.51 or 7.0.100 or later will need to make small changes to their configurations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1938
- https://lists.apache.org/thread.html/re5eecbe5bf967439bafeeaa85987b3a43f0e6efe06b6976ee768cde2@%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/re5eecbe5bf967439bafeeaa85987b3a43f0e6efe06b6976ee768cde2%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rd50baccd1bbb96c2327d5a8caa25a49692b3d68d96915bd1cfbb9f8b@%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rd50baccd1bbb96c2327d5a8caa25a49692b3d68d96915bd1cfbb9f8b%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rd0774c95699d5aeb5e16e9a600fb2ea296e81175e30a62094e27e3e7@%3Ccommits.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/rd0774c95699d5aeb5e16e9a600fb2ea296e81175e30a62094e27e3e7%40%3Ccommits.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/rce2af55f6e144ffcdc025f997eddceb315dfbc0b230e3d750a7f7425@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/rce2af55f6e144ffcdc025f997eddceb315dfbc0b230e3d750a7f7425%40%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/rcd5cd301e9e7e39f939baf2f5d58704750be07a5e2d3393e40ca7194@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/rcd5cd301e9e7e39f939baf2f5d58704750be07a5e2d3393e40ca7194%40%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/rc068e824654c4b8bd4f2490bec869e29edbfcd5dfe02d47cbf7433b2@%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/rc068e824654c4b8bd4f2490bec869e29edbfcd5dfe02d47cbf7433b2%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/rbdb1d2b651a3728f0ceba9e0853575b6f90296a94a71836a15f7364a@%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/rbdb1d2b651a3728f0ceba9e0853575b6f90296a94a71836a15f7364a%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/rb2fc890bef23cbc7f343900005fe1edd3b091cf18dada455580258f9@%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb2fc890bef23cbc7f343900005fe1edd3b091cf18dada455580258f9%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb1c0fb105ce2b93b7ec6fc1b77dd208022621a91c12d1f580813cfed@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rb1c0fb105ce2b93b7ec6fc1b77dd208022621a91c12d1f580813cfed%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rad36ec6a1ffc9e43266b030c22ceeea569243555d34fb4187ff08522@%3Cnotifications.ofbiz.apache.org%3E
