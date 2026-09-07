# [M] Apache CXF's WS-Transfer module has an insecure XML parser configuration

## Summary
Severity: Medium
Advisory: GHSA-vmm5-fjgx-2jhp
CVE: CVE-2026-44618
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-vmm5-fjgx-2jhp
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-ws-transfer` — affected >=4.2.0 <4.2.1
- Maven: `org.apache.cxf:cxf-rt-ws-transfer` — affected >=4.1.0 <4.1.6
- Maven: `org.apache.cxf:cxf-rt-ws-transfer` — affected >=0 <3.6.11

## Details
Insecure XML parser configuration in Apache CXF's WS-Transfer module may allow attackers to perform XXE attacks.
Users are recommended to upgrade to versions 4.2.1, 4.1.6 or 3.6.11, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44618
- https://github.com/apache/cxf
- https://lists.apache.org/thread/c7vb015f8ljmjl44030mn0yfq71f7sd7
- http://www.openwall.com/lists/oss-security/2026/05/22/8
