# [H] JLSEC-2026-137

## Summary
Severity: High
Advisory: JLSEC-2026-137
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-137
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=0 <3.4.4+0

## Details
Academy Software Foundation OpenEXR EXR File Parsing Heap-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Academy Software Foundation OpenEXR. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of EXR files. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a heap-based buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-27948.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-25-991/
