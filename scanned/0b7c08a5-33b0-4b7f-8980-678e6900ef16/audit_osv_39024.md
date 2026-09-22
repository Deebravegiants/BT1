# [C] ksmbd: fix use-after-free in smb_lazy_parent_lease_break_close()

## Summary
Severity: Critical
Advisory: CVE-2026-43379
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43379
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.130, >=6.7.0 <6.12.78, >=6.9.0 <6.18.19, >=6.13.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in smb_lazy_parent_lease_break_close()

opinfo pointer obtained via rcu_dereference(fp->f_opinfo) is being
accessed after rcu_read_unlock() has been called. This creates a
race condition where the memory could be freed by a concurrent
writer between the unlock and the subsequent pointer dereferences
(opinfo->is_lease, etc.), leading to a use-after-free.

## References
- https://git.kernel.org/stable/c/960699317d39f46611f4ebeb69edc567c1f4e6b6
- https://git.kernel.org/stable/c/b3568347c51c46e2cabc356bc34676df98296619
- https://git.kernel.org/stable/c/bf4d66d72e4a9e268c1012c331ce9eaedb5e2086
- https://git.kernel.org/stable/c/dbbd328cf58261ca239756fe1c0d10c9518d3399
- https://git.kernel.org/stable/c/eac3361e3d5dd8067b3258c69615888eb45e9f25
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43379.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43379
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
