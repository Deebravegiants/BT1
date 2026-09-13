# [H] CVE-2023-42118

## Summary
Severity: High
Advisory: CVE-2023-42118
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-42118
Type: osv

## Details
Exim libspf2 Integer Underflow Remote Code Execution Vulnerability. This vulnerability allows network-adjacent attackers to execute arbitrary code on affected installations of Exim libspf2. Authentication is not required to exploit this vulnerability. 

The specific flaw exists within the parsing of SPF macros. When parsing SPF macros, the process does not properly validate user-supplied data, which can result in an integer underflow before writing to memory. An attacker can leverage this vulnerability to execute code in the context of the service account.
. Was ZDI-CAN-17578.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-23-1472/
- http://www.openwall.com/lists/oss-security/2025/03/28/1
