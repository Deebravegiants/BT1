# [C] CVE-2017-0028

## Summary
Severity: Critical
Advisory: CVE-2017-0028
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-0028
Type: osv

## Details
A remote code execution vulnerability exists when Microsoft scripting engine improperly accesses objects in memory. The vulnerability could corrupt memory in a way that enables an attacker to execute arbitrary code in the context of the current user. An attacker who successfully exploited the vulnerability could gain the same user rights as the current user, aka "Scripting Engine Memory Corruption Vulnerability."

## References
- https://github.com/Microsoft/ChakraCore/commit/402f3d967c0a905ec5b9ca9c240783d3f2c15724
