# [H] sched_ext: bpf_iter_scx_dsq_new() should always initialize iterator

## Summary
Severity: High
Advisory: CVE-2025-38012
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38012
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.30, >=6.13.0 <6.14.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched_ext: bpf_iter_scx_dsq_new() should always initialize iterator

BPF programs may call next() and destroy() on BPF iterators even after new()
returns an error value (e.g. bpf_for_each() macro ignores error returns from
new()). bpf_iter_scx_dsq_new() could leave the iterator in an uninitialized
state after an error return causing bpf_iter_scx_dsq_next() to dereference
garbage data. Make bpf_iter_scx_dsq_new() always clear $kit->dsq so that
next() and destroy() become noops.

## References
- https://git.kernel.org/stable/c/0102989af4c334d1d98b2a0fd4d61a5152e39b72
- https://git.kernel.org/stable/c/255dd31bfc4a67a19b1fc2cd130a50284dadfe3a
- https://git.kernel.org/stable/c/428dc9fc0873989d73918d4a9cc22745b7bbc799
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38012.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38012
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
