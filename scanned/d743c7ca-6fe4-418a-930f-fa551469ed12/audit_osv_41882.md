# [H] cgroup/rstat: validate cpu before css_rstat_cpu() access

## Summary
Severity: High
Advisory: CVE-2026-64036
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64036
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

cgroup/rstat: validate cpu before css_rstat_cpu() access

css_rstat_updated() is exposed as a BPF kfunc and accepts a
caller-provided cpu argument. The function uses cpu for per-cpu rstat
lookups without checking whether it refers to a valid possible CPU.

A BPF iter/cgroup program with CAP_BPF and CAP_PERFMON can pass an
invalid cpu value. On an unfixed UBSCAN_BOUNDS test kernel, cpu ==
0x7fffffff triggers:

  UBSAN: array-index-out-of-bounds in kernel/cgroup/rstat.c:31:9
  index 2147483647 is out of range for type 'long unsigned int [64]'
  Call Trace:
    css_rstat_updated
    bpf_iter_run_prog
    cgroup_iter_seq_show
    bpf_seq_read

Add cpu validation to the BPF-facing css_rstat_updated() kfunc and
move the common implementation to __css_rstat_updated() for in-kernel
callers.

## References
- https://git.kernel.org/stable/c/6a01413a4e8fcb0263d7bef5075c5f8f4eb3a8b6
- https://git.kernel.org/stable/c/8817005efbdfdf5d4e4814cb5dc52b53d12917d7
- https://git.kernel.org/stable/c/fd2bd9fa7700ddf28296486b2598cff2f80cc819
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64036.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64036
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
