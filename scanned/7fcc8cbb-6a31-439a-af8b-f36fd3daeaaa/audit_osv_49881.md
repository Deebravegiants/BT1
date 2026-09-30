# [M] CVE-2019-20806

## Summary
Severity: Medium
Advisory: CVE-2019-20806
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-27
Source: https://osv.dev/vulnerability/CVE-2019-20806
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.2. There is a NULL pointer dereference in tw5864_handle_frame() in drivers/media/pci/tw5864/tw5864-video.c, which may cause denial of service, aka CID-2e7682ebfc75.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2
- https://security.netapp.com/advisory/ntap-20200619-0001/
- https://www.debian.org/security/2020/dsa-4698
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2e7682ebfc750177a4944eeb56e97a3f05734528
- https://github.com/torvalds/linux/commit/2e7682ebfc750177a4944eeb56e97a3f05734528
