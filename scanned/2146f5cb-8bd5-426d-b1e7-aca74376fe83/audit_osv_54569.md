# [H] CVE-2024-11477

## Summary
Severity: High
Advisory: CVE-2024-11477
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-22
Source: https://osv.dev/vulnerability/CVE-2024-11477
Type: osv

## Details
7-Zip Zstandard Decompression Integer Underflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of 7-Zip. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the implementation of Zstandard decompression. The issue results from the lack of proper validation of user-supplied data, which can result in an integer underflow before writing to memory. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-24346.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-24-1532/
- https://security.netapp.com/advisory/ntap-20250214-0007/
