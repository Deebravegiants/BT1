# [H] CVE-2023-2163

## Summary
Severity: High
Advisory: CVE-2023-2163
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-09-20
Source: https://osv.dev/vulnerability/CVE-2023-2163
Type: osv

## Details
Incorrect verifier pruning in BPF in Linux Kernel >=5.4 leads to unsafe
code paths being incorrectly marked as safe, resulting in arbitrary read/write in
kernel memory, lateral privilege escalation, and container escape.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=71b547f561247897a0a14f3082730156c0533fed
- https://bughunters.google.com/blog/6303226026131456/a-deep-dive-into-cve-2023-2163-how-we-found-and-fixed-an-ebpf-linux-kernel-vulnerability
