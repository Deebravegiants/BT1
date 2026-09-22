# [M] CVE-2022-3646

## Summary
Severity: Medium
Advisory: CVE-2022-3646
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-3646
Type: osv

## Details
A vulnerability, which was classified as problematic, has been found in Linux Kernel. This issue affects the function nilfs_attach_log_writer of the file fs/nilfs2/segment.c of the component BPF. The manipulation leads to memory leak. The attack may be initiated remotely. It is recommended to apply a patch to fix this issue. The identifier VDB-211961 was assigned to this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://vuldb.com/?id.211961
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=d0d51a97063db4704a5ef6bc978dddab1636a306
