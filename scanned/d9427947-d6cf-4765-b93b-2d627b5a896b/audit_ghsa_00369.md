# [M] In Apache PDFBox a carefully crafted PDF file can trigger an extremely long running computation

## Summary
Severity: Medium
Advisory: GHSA-gx96-vgf7-hwfg
CVE: CVE-2018-11797
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-gx96-vgf7-hwfg
Type: github-advisory

## Affected
- Maven: `org.apache.pdfbox:pdfbox` — affected >=1.8.0 <1.8.16
- Maven: `org.apache.pdfbox:pdfbox` — affected >=2.0.0 <2.0.12

## Details
In Apache PDFBox 1.8.0 to 1.8.15 and 2.0.0RC1 to 2.0.11, a carefully crafted PDF file can trigger an extremely long running computation when parsing the page tree.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11797
- https://github.com/advisories/GHSA-gx96-vgf7-hwfg
- https://lists.apache.org/thread.html/645574bc50b886d39c20b4065d51ccb1cd5d3a6b4750a22edbb565eb@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/a9760973a873522f4d4c0a99916ceb74f361d91006b663a0a418d34a@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r54594251369e14c185da9662a5340a52afbbdf75d61c9c3a69c8f2e8@%3Cdev.pdfbox.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2018/10/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6HKVPTJWZGUB4MH4AAOWMRJHRDBYFHGJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/POPOGHJ5CVMUVCRQU7APBAN5IVZGZFDX
- https://www.oracle.com/security-alerts/cpuapr2020.html
