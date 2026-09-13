# [M] CVE-2018-10187

## Summary
Severity: Medium
Advisory: CVE-2018-10187
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-17
Source: https://osv.dev/vulnerability/CVE-2018-10187
Type: osv

## Details
In radare2 2.5.0, there is a heap-based buffer over-read in the dalvik_op function (libr/anal/p/anal_dalvik.c). Remote attackers could leverage this vulnerability to cause a denial of service via a crafted DEX file. Note that this issue is different from CVE-2018-8809, which was patched earlier.

## References
- https://github.com/radare/radare2/issues/9913
