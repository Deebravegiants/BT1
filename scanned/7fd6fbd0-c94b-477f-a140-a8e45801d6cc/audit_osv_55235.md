# [H] CVE-2025-14936

## Summary
Severity: High
Advisory: CVE-2025-14936
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-14936
Type: osv

## Details
NSF Unidata NetCDF-C Attribute Name Stack-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of NSF Unidata NetCDF-C. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of attribute names. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length stack-based buffer. An attacker can leverage this vulnerability to execute code in the context of the current user. Was ZDI-CAN-27269.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-25-1155/
