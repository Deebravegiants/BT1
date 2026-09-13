# [M] Moderate severity vulnerability that affects org.apache.struts:struts2-rest-plugin

## Summary
Severity: Medium
Advisory: GHSA-xcrm-qpp8-hcw4
CVE: CVE-2017-15707
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-xcrm-qpp8-hcw4
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-rest-plugin` — affected >=2.5.0 <2.5.16

## Details
In Apache Struts 2.5 to 2.5.14, the REST Plugin is using an outdated JSON-lib library which is vulnerable and allow perform a DoS attack using malicious request with specially crafted JSON payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15707
- https://cwiki.apache.org/confluence/display/WW/S2-054
- https://github.com/advisories/GHSA-xcrm-qpp8-hcw4
- https://security.netapp.com/advisory/ntap-20171214-0001
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.securityfocus.com/bid/102021
- http://www.securitytracker.com/id/1039946
