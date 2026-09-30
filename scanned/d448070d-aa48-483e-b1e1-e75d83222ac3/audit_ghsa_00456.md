# [H] Apache Struts REST Plugin can potentially allow a DoS attack

## Summary
Severity: High
Advisory: GHSA-38cr-2ph5-frr9
CVE: CVE-2018-1327
CWE: CWE-91
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-38cr-2ph5-frr9
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-rest-plugin` — affected >=2.1.1 <2.5.16

## Details
The Apache Struts REST Plugin is using XStream library which is vulnerable and allow perform a DoS attack when using a malicious request with specially crafted XML payload. Upgrade to the Apache Struts version 2.5.16 and switch to an optional Jackson XML handler as described here http://struts.apache.org/plugins/rest/#custom-contenttypehandlers. Another option is to implement a custom XML handler based on the Jackson XML handler from the Apache Struts 2.5.16.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1327
- https://github.com/apache/struts/commit/4260bee634cb606be6071bce2383fddb510608aa
- https://github.com/apache/struts/commit/67ecf3a21608e20449bcb7895b22204b400fecd4
- https://github.com/apache/struts/commit/9260720568cee9e868d2899228eceed0c3359323
- https://cwiki.apache.org/confluence/display/WW/S2-056
- https://github.com/apache/struts
- https://lists.apache.org/thread.html/r02c2d634fa74209d941c90f9a4cd36a6f12366ca65f9b90446ff2de3@%3Cissues.struts.apache.org%3E
- https://lists.apache.org/thread.html/rf482c101a88445d73cc2e89dbf7f16ae00a4aa79a544a1e72b2326db@%3Cissues.struts.apache.org%3E
- https://security.netapp.com/advisory/ntap-20180330-0001
- https://web.archive.org/web/20200227124859/http://www.securityfocus.com/bid/103516
- https://web.archive.org/web/20200923124543/http://www.securitytracker.com/id/1040575
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
