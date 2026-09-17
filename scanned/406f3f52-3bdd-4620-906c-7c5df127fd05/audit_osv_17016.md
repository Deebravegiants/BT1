# [M] CVE-2020-11102

## Summary
Severity: Medium
Advisory: CVE-2020-11102
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2020-04-06
Source: https://osv.dev/vulnerability/CVE-2020-11102
Type: osv

## Details
hw/net/tulip.c in QEMU 4.2.0 has a buffer overflow during the copying of tx/rx buffers because the frame size is not validated against the r/w data length.

## References
- http://www.openwall.com/lists/oss-security/2020/04/06/1
- https://lists.gnu.org/archive/html/qemu-devel/2020-03/msg08322.html
- https://security.gentoo.org/glsa/202005-02
