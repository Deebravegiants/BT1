# [M] CVE-2019-6290

## Summary
Severity: Medium
Advisory: CVE-2019-6290
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2019-6290
Type: osv

## Details
An infinite recursion issue was discovered in eval.c in Netwide Assembler (NASM) through 2.14.02. There is a stack exhaustion problem resulting from infinite recursion in the functions expr, rexp, bexpr and cexpr in certain scenarios involving lots of '{' characters. Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted asm file.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392548
