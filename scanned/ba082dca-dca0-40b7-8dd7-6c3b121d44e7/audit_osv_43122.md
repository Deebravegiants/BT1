# [H] ksmbd: fix use-after-free in same_client_has_lease()

## Summary
Severity: High
Advisory: CVE-2026-72492
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72492
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in same_client_has_lease()

same_client_has_lease() returns an opinfo pointer from ci->m_op_list
after dropping ci->m_lock without taking a reference.

smb_grant_oplock() then dereferences that pointer in copy_lease() and
when checking breaking_cnt. A concurrent close can remove the old lease
from ci->m_op_list and drop the last reference before the caller uses
the returned pointer, leading to a use-after-free.

Take a reference when same_client_has_lease() selects an existing lease,
drop any previous match while scanning, and release the returned
reference in smb_grant_oplock() after copying the lease state.

## References
- https://git.kernel.org/stable/c/09634cd055d9bd8dd167995ea52bcd8028dd5dac
- https://git.kernel.org/stable/c/0ff82a9cf9312678d8bc4edeef0b6e82659ac12a
- https://git.kernel.org/stable/c/35d3d6ff2bc1e7aaecb15d5377ebbd6227acae0d
- https://git.kernel.org/stable/c/65b655f65c3ca1ab5d598d3832bb0ff531725858
- https://git.kernel.org/stable/c/79c7c59bb519db6f5a2a151965e825ec725614cc
- https://git.kernel.org/stable/c/7c3264d273d524aa6adcce23c01087271f13586f
- https://git.kernel.org/stable/c/aaa3bb2bbf2ccbfea9e4e0b9dabf3afc60b50cd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72492.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72492
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
