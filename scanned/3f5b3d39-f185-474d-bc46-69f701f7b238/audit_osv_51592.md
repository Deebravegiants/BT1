# [M] CVE-2021-34557

## Summary
Severity: Medium
Advisory: CVE-2021-34557
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2021-34557
Type: osv

## Details
XScreenSaver 5.45 can be bypassed if the machine has more than ten disconnectable video outputs. A buffer overflow in update_screen_layout() allows an attacker to bypass the standard screen lock authentication mechanism by crashing XScreenSaver. The attacker must physically disconnect many video outputs.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TC4QB7TRS4GS7LDXQQ4PC6J3LVFJYISV/
- http://www.openwall.com/lists/oss-security/2021/06/11/1
- https://github.com/QubesOS/qubes-issues/issues/6595
- https://github.com/QubesOS/qubes-xscreensaver/blob/master/0001-Fix-updating-outputs-info.patch
- https://www.openwall.com/lists/oss-security/2021/06/05/1
- http://www.openwall.com/lists/oss-security/2021/07/06/2
- https://github.com/QubesOS/qubes-secpack/blob/master/QSBs/qsb-068-2021.txt
