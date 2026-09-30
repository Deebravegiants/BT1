# [H] CVE-2017-0152

## Summary
Severity: High
Advisory: CVE-2017-0152
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-0152
Type: osv

## Details
A remote code execution vulnerability exists in the way affected Microsoft scripting engine render when handling objects in memory in Microsoft browsers. The vulnerability could corrupt memory in such a way that an attacker could execute arbitrary code in the context of the current user. An attacker who successfully exploited the vulnerability could gain the same user rights as the current user, aka "Scripting Engine Memory Corruption Vulnerability."

## References
- https://github.com/Microsoft/ChakraCore/commit/9da019424601325a6e95e6be0fa03d7d21d0b517
