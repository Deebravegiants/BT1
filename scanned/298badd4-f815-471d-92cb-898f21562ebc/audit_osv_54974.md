# [H] CVE-2024-7539

## Summary
Severity: High
Advisory: CVE-2024-7539
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-06
Source: https://osv.dev/vulnerability/CVE-2024-7539
Type: osv

## Details
oFono CUSD Stack-based Buffer Overflow Code Execution Vulnerability. This vulnerability allows local attackers to execute arbitrary code on affected installations of oFono. An attacker must first obtain the ability to execute code on the target modem in order to exploit this vulnerability.

The specific flaw exists within the parsing of responses from AT+CUSD commands. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a stack-based buffer. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-23195.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-24-1079/
