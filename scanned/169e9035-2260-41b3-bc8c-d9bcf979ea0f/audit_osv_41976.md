# [H] sched_ext: Avoid UAF in scx_root_enable_workfn() init failure path

## Summary
Severity: High
Advisory: CVE-2026-64226
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64226
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched_ext: Avoid UAF in scx_root_enable_workfn() init failure path

In scx_root_enable_workfn(), put_task_struct(p) is called before scx_error()
dereferences p->comm and p->pid. If the iterator's reference is the last
drop, the task is freed synchronously and the deref becomes a UAF.

Move put_task_struct() past scx_error().

## References
- https://git.kernel.org/stable/c/45c7c4e3db8b700307313c035ea08be829a7f21b
- https://git.kernel.org/stable/c/57e19ba3f58a67eb924022a5a60b67fd08e5cbbd
- https://git.kernel.org/stable/c/9a415cc53711f2238e0f0ca8a6bcc796c003b127
- https://git.kernel.org/stable/c/cf396941901858b0de426cdcd3974eea6a02c98c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64226.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64226
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
