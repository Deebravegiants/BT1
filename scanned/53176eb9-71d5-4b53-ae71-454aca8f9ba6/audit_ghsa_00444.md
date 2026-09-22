# [H] Apache Struts allows entering a custom URL in a form field if built-in URLValidator is used

## Summary
Severity: High
Advisory: GHSA-x5x7-3v85-wpc4
CVE: CVE-2017-9804
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-x5x7-3v85-wpc4
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.3.7 <2.3.34
- Maven: `org.apache.struts:struts2-core` — affected >=2.5.0 <2.5.13

## Details
In Apache Struts 2.3.7 through 2.3.33 and 2.5 through 2.5.12, if an application allows entering a URL in a form field and built-in URLValidator is used, it is possible to prepare a special URL which will be used to overload server process when performing validation of the URL.  NOTE: this vulnerability exists because of an incomplete fix for S2-047 / CVE-2017-7672.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9804
- https://github.com/apache/struts/commit/418a20c0594f23764fe29ced400c1219239899a
- https://github.com/apache/struts
- https://security.netapp.com/advisory/ntap-20180629-0001
- https://struts.apache.org/docs/s2-050.html
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20170907-struts2
- https://web.archive.org/web/20171113165852/http://www.securityfocus.com/bid/100612
- https://web.archive.org/web/20201021075553/http://www.securitytracker.com/id/1039261
- http://www.arubanetworks.com/assets/alert/ARUBA-PSA-2017-003.txt
- http://www.oracle.com/technetwork/security-advisory/alert-cve-2017-9805-3889403.html
