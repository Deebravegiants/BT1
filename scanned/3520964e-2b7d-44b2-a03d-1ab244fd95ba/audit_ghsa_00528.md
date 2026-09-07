# [H] The REST Plugin in Apache Struts is using an outdated XStream library

## Summary
Severity: High
Advisory: GHSA-vwxj-6m5m-rrvh
CVE: CVE-2017-9793
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-vwxj-6m5m-rrvh
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-rest-plugin` — affected >=0 <2.3.34
- Maven: `org.apache.struts:struts2-rest-plugin` — affected >=2.5.0 <2.5.13

## Details
The REST Plugin in Apache Struts 2.3.7 through 2.3.33 and 2.5 through 2.5.12 is using an outdated XStream library which is vulnerable and allow perform a DoS attack using malicious request with specially crafted XML payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9793
- https://github.com/advisories/GHSA-vwxj-6m5m-rrvh
- https://security.netapp.com/advisory/ntap-20180629-0001
- https://struts.apache.org/docs/s2-051.html
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20170907-struts2
- http://www.brocade.com/content/dam/common/documents/content-types/security-bulletin/brocade-security-advisory-2017-429.htm
- http://www.oracle.com/technetwork/security-advisory/alert-cve-2017-9805-3889403.html
- http://www.securityfocus.com/bid/100611
- http://www.securitytracker.com/id/1039262
