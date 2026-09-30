# [M] CVE-2018-13250

## Summary
Severity: Medium
Advisory: CVE-2018-13250
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-13250
Type: osv

## Details
libming 0.4.8 has a NULL pointer dereference in the getString function of the decompile.c file, related to decompileSTRINGCONCAT. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted swf file.

## References
- https://github.com/libming/libming/issues/147
