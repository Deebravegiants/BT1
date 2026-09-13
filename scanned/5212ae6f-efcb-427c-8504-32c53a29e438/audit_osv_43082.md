# [H] bpf: Fix effective prog array index with BPF_F_PREORDER

## Summary
Severity: High
Advisory: CVE-2026-72427
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72427
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.15.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix effective prog array index with BPF_F_PREORDER

replace_effective_prog() and purge_effective_progs() located the slot in
the effective array by walking the program hlist and counting entries
linearly. That count does not match the array layout: compute_effective_
progs() places BPF_F_PREORDER programs at the front (ancestor cgroup
first, attach order within a cgroup) and the rest after them (descendant
cgroup first). So when a preorder program is present, the linear hlist
position no longer equals the program's index in the effective array.

For replace_effective_prog() (bpf_link_update()) this overwrote the
wrong slot, corrupting the effective order. For purge_effective_progs(),
it could dummy out a slot belonging to a different program and leave the
detached program in the array while bpf_prog_put() drops its reference,
i.e. a use-after-free.

Fix both by replaying compute_effective_progs()'s placement (including
the per-cgroup preorder reversal) in a shared effective_prog_pos()
helper. Identify the entry by its struct bpf_prog_list pointer rather
than by (prog, link) value, so the lookup resolves to exactly the
attachment the syscall selected even when the same bpf_prog is attached
to several cgroups in the hierarchy.

## References
- https://git.kernel.org/stable/c/41b4320b84fdafe1ab586b06453d30d50415db59
- https://git.kernel.org/stable/c/525e408c27ae714e538b8c608c3a974df3ab6c92
- https://git.kernel.org/stable/c/9697db03e010391c55ae75192cbdf30c5a72c114
- https://git.kernel.org/stable/c/b584f107ab90222bd825dcb4c5977326ff684109
- https://git.kernel.org/stable/c/f08aaee3152d0dfc578b3f2586932d82062701dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72427.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72427
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
