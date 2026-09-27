# [M] CVE-2019-6291

## Summary
Severity: Medium
Advisory: CVE-2019-6291
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2019-6291
Type: osv

## Details
An issue was discovered in the function expr6 in eval.c in Netwide Assembler (NASM) through 2.14.02. There is a stack exhaustion problem caused by the expr6 function making recursive calls to itself in certain scenarios involving lots of '!' or '+' or '-' characters. Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted asm file.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392549
