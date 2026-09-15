# [H] ksmbd: bound DACL dedup walk to copied ACEs

## Summary
Severity: High
Advisory: CVE-2026-68098
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68098
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: bound DACL dedup walk to copied ACEs

set_ntacl_dacl() can stop copying ACEs before consuming the full input
DACL when size accounting overflows.

When that happens, num_aces reflects only the ACEs that were actually
copied into the output DACL, but set_posix_acl_entries_dacl() still
receives nt_num_aces and uses it to walk the existing ACE array during
dedup.

That makes the dedup walk scan past the copied ACE array and inspect
buffer tail that does not contain valid ACEs.

Split the two meanings currently carried by the NT ACE count. Pass the
number of copied NT ACEs to bound the dedup walk, and preserve the
original "input DACL had NT ACEs" state separately for the
Everyone/default ACL fallback.

This keeps the dedup walk aligned with the ACEs that are actually
present in the rebuilt DACL.

## References
- https://git.kernel.org/stable/c/58d97fcd0bf1aee694e244cc28635b9df95b543b
- https://git.kernel.org/stable/c/6d9d7aa4a2c99c31acfa28921c30b684110cf66c
- https://git.kernel.org/stable/c/a0ebdaa79e10210d4e8ed9fe138e8f4d569719e3
- https://git.kernel.org/stable/c/b057a851129c6a084e7e393b62ca3abf6c2660bc
- https://git.kernel.org/stable/c/f1eba60db813ec28732bf18b5f0a67ebac9c3100
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68098.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68098
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
