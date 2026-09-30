# [M] Allocation of Resources Without Limits or Throttling in iText

## Summary
Severity: Medium
Advisory: GHSA-hhh6-cm2m-3fhc
CVE: CVE-2022-24196
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-02
Source: https://github.com/advisories/GHSA-hhh6-cm2m-3fhc
Type: github-advisory

## Affected
- Maven: `com.itextpdf:itext7-core` — affected >=0 <7.1.18

## Details
iText v7.1.17 was discovered to contain an out-of-memory error via the component readStreamBytesRaw, which allows attackers to cause a Denial of Service (DoS) via a crafted PDF file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24196
- https://github.com/itext/itext7/pull/78
- https://github.com/itext/itext7/pull/78#issuecomment-1089279222
- https://github.com/itext/itext7
- https://github.com/itext/itext7/releases/tag/7.1.18
