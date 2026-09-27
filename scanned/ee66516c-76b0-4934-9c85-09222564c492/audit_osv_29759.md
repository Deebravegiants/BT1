# [M] Apache Tomcat Connectors: mod_jk: local users can view and modify configuration

## Summary
Severity: Medium
Advisory: CVE-2024-46544
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-09-23
Source: https://osv.dev/vulnerability/CVE-2024-46544
Type: osv

## Details
Incorrect Default Permissions vulnerability in Apache Tomcat Connectors allows local users to view and modify shared memory containing mod_jk configuration which may lead to information disclosure and/or denial of service.

This issue affects Apache Tomcat Connectors: from 1.2.9-beta through 1.2.49. Only mod_jk on Unix like systems is affected. Neither the ISAPI redirector nor mod_jk on Windows is affected.

Users are recommended to upgrade to version 1.2.50, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/09/23/1
- https://lists.debian.org/debian-lts-announce/2024/10/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46544.json
- https://lists.apache.org/thread/q1gp7cc38hs1r8gj8gfnopwznd5fpr4d
- https://nvd.nist.gov/vuln/detail/CVE-2024-46544
