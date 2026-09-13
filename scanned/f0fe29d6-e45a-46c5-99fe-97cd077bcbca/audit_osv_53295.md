# [H] CVE-2022-3649

## Summary
Severity: High
Advisory: CVE-2022-3649
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-3649
Type: osv

## Details
A vulnerability was found in Linux Kernel. It has been classified as problematic. Affected is the function nilfs_new_inode of the file fs/nilfs2/inode.c of the component BPF. The manipulation leads to use after free. It is possible to launch the attack remotely. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-211992.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://security.netapp.com/advisory/ntap-20230214-0009/
- https://vuldb.com/?id.211992
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=d325dc6eb763c10f591c239550b8c7e5466a5d09
