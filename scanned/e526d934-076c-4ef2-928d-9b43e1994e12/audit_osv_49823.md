# [M] CVE-2019-19526

## Summary
Severity: Medium
Advisory: CVE-2019-19526
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19526
Type: osv

## Details
In the Linux kernel before 5.3.9, there is a use-after-free bug that can be caused by a malicious USB device in the drivers/nfc/pn533/usb.c driver, aka CID-6af3aa57a098.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.9
- https://usn.ubuntu.com/4226-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6af3aa57a0984e061f61308fe181a9a12359fecc
