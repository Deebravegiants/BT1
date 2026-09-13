# [M] CVE-2019-19966

## Summary
Severity: Medium
Advisory: CVE-2019-19966
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-25
Source: https://osv.dev/vulnerability/CVE-2019-19966
Type: osv

## Details
In the Linux kernel before 5.1.6, there is a use-after-free in cpia2_exit() in drivers/media/usb/cpia2/cpia2_v4l.c that will cause denial of service, aka CID-dea37a972655.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://security.netapp.com/advisory/ntap-20200204-0002/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.6
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=dea37a97265588da604c6ba80160a287b72c7bfd
