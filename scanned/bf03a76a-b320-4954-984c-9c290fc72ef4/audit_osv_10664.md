# [M] CVE-2017-18043

## Summary
Severity: Medium
Advisory: CVE-2017-18043
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-31
Source: https://osv.dev/vulnerability/CVE-2017-18043
Type: osv

## Details
Integer overflow in the macro ROUND_UP (n, d) in Quick Emulator (Qemu) allows a user to cause a denial of service (Qemu process crash).

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=2098b073f398cd628c09c5a78537a6854
- http://www.openwall.com/lists/oss-security/2018/01/19/1
- http://www.securityfocus.com/bid/102759
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://usn.ubuntu.com/3575-1/
- https://www.debian.org/security/2018/dsa-4213
