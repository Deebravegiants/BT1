# [H] CVE-2021-41864

## Summary
Severity: High
Advisory: CVE-2021-41864
Aliases: A-202511260, PUB-A-202511260
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-02
Source: https://osv.dev/vulnerability/CVE-2021-41864
Type: osv

## Details
prealloc_elems_and_freelist in kernel/bpf/stackmap.c in the Linux kernel before 5.14.12 allows unprivileged users to trigger an eBPF multiplication integer overflow with a resultant out-of-bounds write.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SYKURLXBB2555ASWMPDNMBUPD6AG2JKQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7BLLVKYAIETEORUPTFO3TR3C33ZPFXQM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LAT3RERO6QBKSPJBNNRWY3D4NCGTFOS7/
- https://www.debian.org/security/2022/dsa-5096
- https://security.netapp.com/advisory/ntap-20211029-0004/
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.12
- https://github.com/torvalds/linux/commit/30e29a9a2bc6a4888335a6ede968b75cd329657a
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf.git/commit/?id=30e29a9a2bc6a4888335a6ede968b75cd329657a
