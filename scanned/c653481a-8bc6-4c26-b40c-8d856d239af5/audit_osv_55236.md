# [H] CVE-2025-15269

## Summary
Severity: High
Advisory: CVE-2025-15269
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-31
Source: https://osv.dev/vulnerability/CVE-2025-15269
Type: osv

## Details
FontForge SFD File Parsing Use-After-Free Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of FontForge. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of SFD files. The issue results from the lack of validating the existence of an object prior to performing operations on the object. An attacker can leverage this vulnerability to execute code in the context of the current user. Was ZDI-CAN-28564.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-25-1195/
