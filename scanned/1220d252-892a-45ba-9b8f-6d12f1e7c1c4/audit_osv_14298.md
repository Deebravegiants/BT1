# [M] CVE-2018-8810

## Summary
Severity: Medium
Advisory: CVE-2018-8810
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/CVE-2018-8810
Type: osv

## Details
In radare2 2.4.0, there is a heap-based buffer over-read in the get_ivar_list_t function of mach0_classes.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted Mach-O file.

## References
- https://github.com/radare/radare2/issues/9727
