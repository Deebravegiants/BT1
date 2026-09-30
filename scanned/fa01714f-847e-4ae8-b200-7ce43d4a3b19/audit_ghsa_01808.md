# [C] Improperly Controlled Modification of Dynamically-Determined Object Attributes in Apache Struts

## Summary
Severity: Critical
Advisory: GHSA-wp4h-pvgw-5727
CVE: CVE-2019-0230
CWE: CWE-1321, CWE-915
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-02
Source: https://github.com/advisories/GHSA-wp4h-pvgw-5727
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.5.22

## Details
Apache Struts 2.0.0 to 2.5.20 forced double OGNL evaluation, when evaluated on raw user input in tag attributes, may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0230
- https://cwiki.apache.org/confluence/display/ww/s2-059
- https://github.com/apache/struts
- https://launchpad.support.sap.com/#/notes/2982840
- https://lists.apache.org/thread.html/r1125f3044a0946d1e7e6f125a6170b58d413ebd4a95157e4608041c7@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r90890afea72a9571d666820b2fe5942a0a5f86be406fa31da3dd0922@%3Cannounce.apache.org%3E
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- http://packetstormsecurity.com/files/160108/Apache-Struts-2.5.20-Double-OGNL-Evaluation.html
- http://packetstormsecurity.com/files/160721/Apache-Struts-2-Forced-Multi-OGNL-Evaluation.html
