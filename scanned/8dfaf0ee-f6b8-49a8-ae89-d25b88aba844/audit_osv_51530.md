# [M] CVE-2021-3178

## Summary
Severity: Medium
Advisory: CVE-2021-3178
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-01-19
Source: https://osv.dev/vulnerability/CVE-2021-3178
Type: osv

## Details
fs/nfsd/nfs3xdr.c in the Linux kernel through 5.10.8, when there is an NFS export of a subdirectory of a filesystem, allows remote attackers to traverse to other parts of the filesystem via READDIRPLUS. NOTE: some parties argue that such a subdirectory export is not intended to prevent this attack; see also the exports(5) no_subtree_check default behavior

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5SGB7TNDVQEOJ7NVTGX56UWHDNQM5TRC/
- https://patchwork.kernel.org/project/linux-nfs/patch/20210111210129.GA11652%40fieldses.org/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=51b2ee7d006a736a9126e8111d1f24e4fd0afaa6
