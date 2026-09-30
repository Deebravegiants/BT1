# [M] CVE-2018-8806

## Summary
Severity: Medium
Advisory: CVE-2018-8806
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/CVE-2018-8806
Type: osv

## Details
In libming 0.4.8, there is a use-after-free in the decompileArithmeticOp function of decompile.c. Remote attackers could use this vulnerability to cause a denial-of-service via a crafted swf file.

## References
- https://github.com/libming/libming/issues/128
