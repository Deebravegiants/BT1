# [M] CVE-2018-16999

## Summary
Severity: Medium
Advisory: CVE-2018-16999
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-13
Source: https://osv.dev/vulnerability/CVE-2018-16999
Type: osv

## Details
Netwide Assembler (NASM) 2.14rc15 has an invalid memory write (segmentation fault) in expand_smacro in preproc.c, which allows attackers to cause a denial of service via a crafted input file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00017.html
- https://bugzilla.nasm.us/show_bug.cgi?id=3392508
