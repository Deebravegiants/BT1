# [H] Apache Tomcat Connectors: Unexpected use of first declared worker in mod_jk for unmapped request

## Summary
Severity: High
Advisory: CVE-2023-41081
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-09-13
Source: https://osv.dev/vulnerability/CVE-2023-41081
Type: osv

## Details
Important: Authentication Bypass CVE-2023-41081

The mod_jk component of Apache Tomcat Connectors in some circumstances, such as when a configuration included "JkOptions +ForwardDirectories" but the configuration did not       provide explicit mounts for all possible proxied requests, mod_jk would       use an implicit mapping and map the request to the first defined worker. Such an implicit mapping could result in the unintended exposure of the status worker and/or bypass security constraints configured in httpd. As of JK 1.2.49, the implicit mapping functionality has been removed and all mappings must now be via explicit configuration. Only mod_jk is affected by this issue. The ISAPI redirector is not affected.

This issue affects Apache Tomcat Connectors (mod_jk only): from 1.2.0 through 1.2.48.

Users are recommended to upgrade to version 1.2.49, which fixes the issue.

History
2023-09-13 Original advisory

2023-09-28 Updated summary

## References
- http://www.openwall.com/lists/oss-security/2023/09/28/7
- https://lists.debian.org/debian-lts-announce/2023/09/msg00027.html
- https://www.openwall.com/lists/oss-security/2023/09/13/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41081.json
- https://lists.apache.org/thread/rd1r26w7271jyqgzr4492tooyt583d8b
- https://nvd.nist.gov/vuln/detail/CVE-2023-41081
