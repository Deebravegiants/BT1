# [H] Apache juddi-client vulnerable to XML External Entity (XXE)

## Summary
Severity: High
Advisory: GHSA-p99p-726h-c8v5
CVE: CVE-2018-1307
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-p99p-726h-c8v5
Type: github-advisory

## Affected
- Maven: `org.apache.juddi:juddi-client` — affected >=3.2 <3.3.5

## Details
In Apache jUDDI 3.2 through 3.3.4, if using the WADL2Java or WSDL2Java classes, which parse a local or remote XML document and then mediates the data structures into UDDI data structures, there are little protections present against entity expansion and DTD type of attacks. Mitigation is to use 3.3.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1307
- https://github.com/advisories/GHSA-p99p-726h-c8v5
- https://issues.apache.org/jira/browse/JUDDI-987
- http://juddi.apache.org/security.html
