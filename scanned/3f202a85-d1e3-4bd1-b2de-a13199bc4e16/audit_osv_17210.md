# [M] CVE-2020-13765

## Summary
Severity: Medium
Advisory: CVE-2020-13765
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2020-06-04
Source: https://osv.dev/vulnerability/CVE-2020-13765
Type: osv

## Details
rom_copy() in hw/core/loader.c in QEMU 4.0 and 4.1.0 does not validate the relationship between two addresses, which allows attackers to trigger an invalid memory copy operation.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=e423455c4f23a1a828901c78fe6d03b7dde79319
- https://lists.debian.org/debian-lts-announce/2020/06/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00020.html
- https://security.netapp.com/advisory/ntap-20200619-0006/
- https://usn.ubuntu.com/4467-1/
- https://www.openwall.com/lists/oss-security/2020/06/03/6
- https://github.com/qemu/qemu/commit/4f1c6cb2f9afafda05eab150fd2bd284edce6676
