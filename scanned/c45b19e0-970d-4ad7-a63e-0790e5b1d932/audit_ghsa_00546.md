# [H] REST Plugin in Apache Struts uses an XStreamHandler with an instance of XStream for deserialization without any type filtering

## Summary
Severity: High
Advisory: GHSA-gg9m-fj3v-r58c
CVE: CVE-2017-9805
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-gg9m-fj3v-r58c
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-rest-plugin` — affected >=2.1.1 <2.3.34
- Maven: `org.apache.struts:struts2-rest-plugin` — affected >=2.5.0 <2.5.13

## Details
The REST Plugin in Apache Struts 2.1.1 through 2.3.x before 2.3.34 and 2.5.x before 2.5.13 uses an XStreamHandler with an instance of XStream for deserialization without any type filtering, which can lead to Remote Code Execution when deserializing XML payloads.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9805
- https://github.com/apache/struts/commit/19494718865f2fb7da5ea363de3822f87fbda26
- https://github.com/apache/struts/commit/6dd6e5cfb7b5e020abffe7e8091bd63fe97c10a
- https://blogs.apache.org/foundation/entry/apache-struts-statement-on-equifax
- https://bugzilla.redhat.com/show_bug.cgi?id=1488482
- https://cwiki.apache.org/confluence/display/WW/S2-052
- https://github.com/apache/struts
- https://lgtm.com/blog/apache_struts_CVE-2017-9805
- https://security.netapp.com/advisory/ntap-20170907-0001
- https://struts.apache.org/docs/s2-052.html
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20170907-struts2
- https://web.archive.org/web/20170909031344/http://www.securityfocus.com/bid/100609
- https://web.archive.org/web/20170922053119/http://www.securitytracker.com/id/1039263
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2017-9805
- https://www.exploit-db.com/exploits/42627
- https://www.kb.cert.org/vuls/id/112992
- http://www.oracle.com/technetwork/security-advisory/alert-cve-2017-9805-3889403.html
- http://www.securityfocus.com/bid/100609
- http://www.securitytracker.com/id/1039263
