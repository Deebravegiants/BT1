# [H] CVE-2023-40481

## Summary
Severity: High
Advisory: CVE-2023-40481
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-40481
Type: osv

## Details
7-Zip SquashFS File Parsing Out-Of-Bounds Write Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of 7-Zip. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of SQFS files. The issue results from the lack of proper validation of user-supplied data, which can result in a write past the end of an allocated buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-18589.

## References
- https://sourceforge.net/p/sevenzip/discussion/45797/thread/713c8a8269/
- https://www.zerodayinitiative.com/advisories/ZDI-23-1164/
