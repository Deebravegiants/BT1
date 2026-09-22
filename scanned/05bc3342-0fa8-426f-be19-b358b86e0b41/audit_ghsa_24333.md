# [H] Improper Preservation of Permissions in Apache Struts

## Summary
Severity: High
Advisory: GHSA-ccp5-gg58-pxfm
CVE: CVE-2019-0233
CWE: CWE-281
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ccp5-gg58-pxfm
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.5.22

## Details
An access permission override in Apache Struts 2.0.0 to 2.5.20 may cause a Denial of Service when performing a file upload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0233
- https://cwiki.apache.org/confluence/display/ww/s2-060
- https://launchpad.support.sap.com/#/notes/2982840
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
