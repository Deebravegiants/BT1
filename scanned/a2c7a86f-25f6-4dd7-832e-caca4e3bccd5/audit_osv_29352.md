# [H] bpf: Fix remap of arena.

## Summary
Severity: High
Advisory: CVE-2024-42075
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42075
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix remap of arena.

The bpf arena logic didn't account for mremap operation. Add a refcnt for
multiple mmap events to prevent use-after-free in arena_vm_close.

## References
- https://git.kernel.org/stable/c/87496a1b01e8e2e399428c0db25e106f7961d01e
- https://git.kernel.org/stable/c/b90d77e5fd784ada62ddd714d15ee2400c28e1cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42075.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42075
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
