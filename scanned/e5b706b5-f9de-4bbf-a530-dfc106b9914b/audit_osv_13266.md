# [M] CVE-2018-18954

## Summary
Severity: Medium
Advisory: CVE-2018-18954
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-15
Source: https://osv.dev/vulnerability/CVE-2018-18954
Type: osv

## Details
The pnv_lpc_do_eccb function in hw/ppc/pnv_lpc.c in Qemu before 3.1 allows out-of-bounds write or read access to PowerNV memory.

## References
- https://seclists.org/bugtraq/2019/May/76
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00042.html
- http://www.securityfocus.com/bid/105920
- https://usn.ubuntu.com/3826-1/
- https://www.debian.org/security/2019/dsa-4454
- http://www.openwall.com/lists/oss-security/2018/11/06/6
- https://lists.gnu.org/archive/html/qemu-devel/2018-11/msg00446.html
