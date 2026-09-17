# [M] CVE-2020-27616

## Summary
Severity: Medium
Advisory: CVE-2020-27616
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/CVE-2020-27616
Type: osv

## Details
ati_2d_blt in hw/display/ati_2d.c in QEMU 4.2.1 can encounter an outside-limits situation in a calculation. A guest can crash the QEMU process.

## References
- https://security.netapp.com/advisory/ntap-20201202-0002/
- http://www.openwall.com/lists/oss-security/2020/11/03/2
- https://lists.nongnu.org/archive/html/qemu-devel/2020-10/msg05018.html
