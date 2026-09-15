# [C] CVE-2017-16845

## Summary
Severity: Critical
Advisory: CVE-2017-16845
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:H)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-16845
Type: osv

## Details
hw/input/ps2.c in Qemu does not validate 'rptr' and 'count' values during guest migration, leading to out-of-bounds access.

## References
- http://www.securityfocus.com/bid/101923
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://usn.ubuntu.com/3575-1/
- https://usn.ubuntu.com/3649-1/
- https://www.debian.org/security/2018/dsa-4213
- https://lists.gnu.org/archive/html/qemu-devel/2017-11/msg02982.html
