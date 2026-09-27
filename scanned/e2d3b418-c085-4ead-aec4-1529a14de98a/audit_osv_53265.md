# [M] CVE-2022-3543

## Summary
Severity: Medium
Advisory: CVE-2022-3543
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3543
Type: osv

## Details
A vulnerability, which was classified as problematic, has been found in Linux Kernel. This issue affects the function unix_sock_destructor/unix_release_sock of the file net/unix/af_unix.c of the component BPF. The manipulation leads to memory leak. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-211043.

## References
- https://vuldb.com/?id.211043
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=7a62ed61367b8fd01bae1e18e30602c25060d824
