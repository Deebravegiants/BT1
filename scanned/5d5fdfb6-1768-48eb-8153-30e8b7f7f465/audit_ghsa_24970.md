# [M] Loop with Unreachable Exit Condition in Apache PDFBox

## Summary
Severity: Medium
Advisory: GHSA-j2xq-pfff-mvgg
CVE: CVE-2018-8036
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j2xq-pfff-mvgg
Type: github-advisory

## Affected
- Maven: `org.apache.pdfbox:pdfbox` — affected >=1.8.0 <1.8.15
- Maven: `org.apache.pdfbox:pdfbox` — affected >=2.0.0RC1 <2.0.11

## Details
In Apache PDFBox 1.8.0 to 1.8.14 and 2.0.0RC1 to 2.0.10, a carefully crafted (or fuzzed) file can trigger an infinite loop which leads to an out of memory exception in Apache PDFBox's AFMParser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8036
- https://access.redhat.com/errata/RHSA-2018:2669
- https://lists.apache.org/thread.html/9f62f742fd4fcd81654a9533b8a71349b064250840592bcd502dcfb6@%3Cusers.pdfbox.apache.org%3E
- https://lists.apache.org/thread.html/r43491b25b2e5c368c34b106a82eff910a5cea3e90de82ad75cc16540@%3Cdev.syncope.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6HKVPTJWZGUB4MH4AAOWMRJHRDBYFHGJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/POPOGHJ5CVMUVCRQU7APBAN5IVZGZFDX
- https://www.oracle.com/security-alerts/cpuapr2020.html
