# [M] Excessive Iteration Denial of Service in Apache PDFBox

## Summary
Severity: Medium
Advisory: GHSA-2h3j-m7gr-25xj
CVE: CVE-2021-27807
CWE: CWE-834
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-2h3j-m7gr-25xj
Type: github-advisory

## Affected
- Maven: `org.apache.pdfbox:pdfbox` — affected >=2.0.0 <2.0.23

## Details
A carefully crafted PDF file can trigger an infinite loop while loading the file. This issue affects Apache PDFBox version 2.0.22 and prior 2.0.x versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27807
- https://github.com/apache/pdfbox/commit/5c5a837140fbb4ef78bb5ef9f29ad537c872c83e
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://svn.apache.org/viewvc?view=revision&revision=1886911
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6PT72QOFDXLJ7PLTN66EMG5EHPTE7TFZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6KDA2U4KL2N3XT3PM4ZJEBBA6JJIH2G4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2AVLKAHFMPH72TTP25INPZPGX5FODK3H
- https://lists.apache.org/thread.html/re1e35881482e07dc2be6058d9b44483457f36133cac67956686ad9b9@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/rc69140d894c6a9c67a8097a25656cce59b46a5620c354ceba10543c3@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/raa35746227f3f8d50fff1db9899524423a718f6f35cd39bd4769fa6c@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/r9ffe179385637b0b5cbdabd0246118005b4b8232909d2d14cd68ccd3@%3Ccommits.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/r818058ff1e4b9f6bef4e5a2e74faff38cb3d3885c1e2db398bc55cfb@%3Cusers.pdfbox.apache.org%3E
- https://lists.apache.org/thread.html/r818058ff1e4b9f6bef4e5a2e74faff38cb3d3885c1e2db398bc55cfb%40%3Cusers.pdfbox.apache.org%3E
- https://lists.apache.org/thread.html/r7ee634c21816c69ce829d0c41f35afa2a53a99bdd3c7cce8644fdc0e@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/r6e067a6d83ccb6892d0ff867bd216704f21fb0b6a854dea34be04f12@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/r5c8e2125d18af184c80f7a986fbe47eaf0d30457cd450133adc235ac@%3Ccommits.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/r54594251369e14c185da9662a5340a52afbbdf75d61c9c3a69c8f2e8@%3Cdev.pdfbox.apache.org%3E
- https://lists.apache.org/thread.html/r4cbc3f6981cd0a1a482531df9d44e4c42a7f63342a7ba78b7bff8a1b@%3Cnotifications.james.apache.org%3E
