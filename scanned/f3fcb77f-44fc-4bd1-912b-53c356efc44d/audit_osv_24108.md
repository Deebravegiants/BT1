# [H] bpf: Fix KASAN use-after-free Read in compute_effective_progs

## Summary
Severity: High
Advisory: CVE-2022-50219
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50219
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.138, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix KASAN use-after-free Read in compute_effective_progs

Syzbot found a Use After Free bug in compute_effective_progs().
The reproducer creates a number of BPF links, and causes a fault
injected alloc to fail, while calling bpf_link_detach on them.
Link detach triggers the link to be freed by bpf_link_free(),
which calls __cgroup_bpf_detach() and update_effective_progs().
If the memory allocation in this function fails, the function restores
the pointer to the bpf_cgroup_link on the cgroup list, but the memory
gets freed just after it returns. After this, every subsequent call to
update_effective_progs() causes this already deallocated pointer to be
dereferenced in prog_list_length(), and triggers KASAN UAF error.

To fix this issue don't preserve the pointer to the prog or link in the
list, but remove it and replace it with a dummy prog without shrinking
the table. The subsequent call to __cgroup_bpf_detach() or
__cgroup_bpf_detach() will correct it.

## References
- https://git.kernel.org/stable/c/1f8ca9c40e6222ce431e9ba5dae3cccce8ef9443
- https://git.kernel.org/stable/c/3527e3cbb84d8868c4d4e91ba55915f96d39ec3d
- https://git.kernel.org/stable/c/4c46091ee985ae84c60c5e95055d779fcd291d87
- https://git.kernel.org/stable/c/6336388715afa419cc97d0255bda3bba1b96b7ca
- https://git.kernel.org/stable/c/be001f9da71eaa3b61e186fb88bde3279728bdca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50219.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50219
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
