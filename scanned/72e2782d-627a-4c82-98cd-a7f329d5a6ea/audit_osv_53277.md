# [M] CVE-2022-3606

## Summary
Severity: Medium
Advisory: CVE-2022-3606
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-3606
Type: osv

## Details
A vulnerability was found in Linux Kernel. It has been classified as problematic. This affects the function find_prog_by_sec_insn of the file tools/lib/bpf/libbpf.c of the component BPF. The manipulation leads to null pointer dereference. It is recommended to apply a patch to fix this issue. The identifier VDB-211749 was assigned to this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00033.html
- https://vuldb.com/?id.211749
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=d0d382f95a9270dcf803539d6781d6bd67e3f5b2
