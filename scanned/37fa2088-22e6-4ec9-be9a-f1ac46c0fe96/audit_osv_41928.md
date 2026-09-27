# [H] lsm: hold cred_guard_mutex for lsm_set_self_attr()

## Summary
Severity: High
Advisory: CVE-2026-64111
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64111
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

lsm: hold cred_guard_mutex for lsm_set_self_attr()

Just as proc_pid_attr_write() already does before calling the LSM
hook. This only matters for SELinux and AppArmor which check
whether the process is being ptraced and if so, whether to
allow the transition.

## References
- https://git.kernel.org/stable/c/4a9b16541ad3faf8bccb398532bf3f8b6bbf1188
- https://git.kernel.org/stable/c/5b906f31e977286888a9e31282589b545b249139
- https://git.kernel.org/stable/c/82d3acee88593e3d9e71cad4b7d6b3cf70de9d07
- https://git.kernel.org/stable/c/a010cadaf5727b8417f62fe9021fcef14a5f9b51
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64111.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64111
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
