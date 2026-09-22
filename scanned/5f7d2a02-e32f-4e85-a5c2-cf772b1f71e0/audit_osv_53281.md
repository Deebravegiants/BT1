# [M] CVE-2022-3621

## Summary
Severity: Medium
Advisory: CVE-2022-3621
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-20
Source: https://osv.dev/vulnerability/CVE-2022-3621
Type: osv

## Details
A vulnerability was found in Linux Kernel. It has been classified as problematic. Affected is the function nilfs_bmap_lookup_at_level of the file fs/nilfs2/inode.c of the component nilfs2. The manipulation leads to null pointer dereference. It is possible to launch the attack remotely. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-211920.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://vuldb.com/?id.211920
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=21a87d88c2253350e115029f14fe2a10a7e6c856
