# [M] CVE-2019-15213

## Summary
Severity: Medium
Advisory: CVE-2019-15213
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2019-15213
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.2.3. There is a use-after-free caused by a malicious USB device in the drivers/media/usb/dvb-usb/dvb-usb-init.c driver.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- http://www.openwall.com/lists/oss-security/2019/08/20/2
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.3
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6cf97230cd5f36b7665099083272595c55d72be7
- https://syzkaller.appspot.com/bug?id=a53c9c9dd2981bfdbfbcbc1ddbd35595eda8bced
