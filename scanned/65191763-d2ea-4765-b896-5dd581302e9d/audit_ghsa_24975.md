# [H] Exposure of Sensitive Information in Apache Pluto

## Summary
Severity: High
Advisory: GHSA-v49x-8hvm-q347
CVE: CVE-2018-1306
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v49x-8hvm-q347
Type: github-advisory

## Affected
- Maven: `org.apache.portals.pluto:pluto-container` — affected >=3.0.0 <3.0.1

## Details
The PortletV3AnnotatedDemo Multipart Portlet war file code provided in Apache Pluto version 3.0.0 could allow a remote attacker to obtain sensitive information, caused by the failure to restrict path information provided during a file upload. An attacker could exploit this vulnerability to obtain configuration data and other sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1306
- https://github.com/apache/portals-pluto
- https://www.exploit-db.com/exploits/45396
- http://portals.apache.org/pluto/security.html
