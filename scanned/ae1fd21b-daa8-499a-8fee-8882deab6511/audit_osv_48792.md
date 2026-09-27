# [M] CVE-2018-14320

## Summary
Severity: Medium
Advisory: CVE-2018-14320
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-09-17
Source: https://osv.dev/vulnerability/CVE-2018-14320
Type: osv

## Details
This vulnerability allows remote attackers to disclose sensitive information on vulnerable installations of PoDoFo. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file. The specific flaw exists within PdfEncoding::ParseToUnicode. The issue results from the lack of proper validation of user-supplied data, which can result in a memory corruption condition. An attacker can leverage this in conjunction with other vulnerabilities to execute arbitrary code in the context of the current process. Was ZDI-CAN-5673.

## References
- https://zerodayinitiative.com/advisories/ZDI-18-1046
