# [M] CVE-2018-16517

## Summary
Severity: Medium
Advisory: CVE-2018-16517
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-16517
Type: osv

## Details
asm/labels.c in Netwide Assembler (NASM) is prone to NULL Pointer Dereference, which allows the attacker to cause a denial of service via a crafted file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00017.html
- https://bugzilla.nasm.us/show_bug.cgi?id=3392513
- http://packetstormsecurity.com/files/152566/Netwide-Assembler-NASM-2.14rc15-Null-Pointer-Dereference.html
- https://fakhrizulkifli.github.io/CVE-2018-16517.html
- https://www.exploit-db.com/exploits/46726/
