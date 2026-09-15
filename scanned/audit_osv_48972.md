# [M] CVE-2018-19209

## Summary
Severity: Medium
Advisory: CVE-2018-19209
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19209
Type: osv

## Details
Netwide Assembler (NASM) 2.14rc15 has a NULL pointer dereference in the function find_label in asm/labels.c that will lead to a DoS attack.

## References
- https://bugzilla.suse.com/show_bug.cgi?id=1115797
- https://repo.or.cz/nasm.git/commitdiff/e996d28c70d45008085322b442b44a9224308548
