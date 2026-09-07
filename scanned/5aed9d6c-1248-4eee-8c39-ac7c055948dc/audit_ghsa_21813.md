# [H] Server-side request forgery (SSRF) in Apache XmlGraphics Commons

## Summary
Severity: High
Advisory: GHSA-fmj2-7wx8-qj4v
CVE: CVE-2020-11988
CWE: CWE-20, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-fmj2-7wx8-qj4v
Type: github-advisory

## Affected
- Maven: `org.apache.xmlgraphics:xmlgraphics-commons` — affected >=0 <2.6

## Details
Apache XmlGraphics Commons 2.4 is vulnerable to server-side request forgery, caused by improper input validation by the XMPParser. By using a specially-crafted argument, an attacker could exploit this vulnerability to cause the underlying server to make arbitrary GET requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11988
- https://github.com/apache/xmlgraphics-commons/commit/57393912eb87b994c7fed39ddf30fb778a275183
- https://github.com/apache/xmlgraphics-commons
- https://issues.apache.org/jira/browse/XGC-122
- https://lists.apache.org/thread.html/r2877ae10e8be56a3c52d03e373512ddd32f16b863f24c2e22f5a5ba2@%3Cdev.poi.apache.org%3E
- https://lists.apache.org/thread.html/r588d05a0790b40a0eb81088252e1e8c1efb99706631421f17038eb05@%3Cdev.poi.apache.org%3E
- https://lists.apache.org/thread.html/ra8f4d6ae402ec020ee3e8c28632c91be131c4d8b4c9c6756a179b12b@%3Cdev.jmeter.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/22HESSYU7T4D6GGENUVEX3X3H6FGBECH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JP4XA56DA3BFNRBBLBXM6ZAI5RUVFA33
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://xmlgraphics.apache.org/security.html
