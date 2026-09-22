# [M] CVE-2019-20810

## Summary
Severity: Medium
Advisory: CVE-2019-20810
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2019-20810
Type: osv

## Details
go7007_snd_init in drivers/media/usb/go7007/snd-go7007.c in the Linux kernel before 5.6 does not call snd_card_free for a failure path, which causes a memory leak, aka CID-9453264ef586.

## References
- https://usn.ubuntu.com/4427-1/
- https://usn.ubuntu.com/4439-1/
- https://usn.ubuntu.com/4440-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00019.html
- https://usn.ubuntu.com/4483-1/
- https://usn.ubuntu.com/4485-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9453264ef58638ce8976121ac44c07a3ef375983
