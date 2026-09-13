# [H] ksmbd: validate inherited ACE SID length

## Summary
Severity: High
Advisory: CVE-2026-43490
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-43490
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.141, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate inherited ACE SID length

smb_inherit_dacl() walks the parent directory DACL loaded from the
security descriptor xattr. It verifies that each ACE contains the fixed
SID header before using it, but does not verify that the variable-length
SID described by sid.num_subauth is fully contained in the ACE.

A malformed inheritable ACE can advertise more subauthorities than are
present in the ACE. compare_sids() may then read past the ACE.
smb_set_ace() also clamps the copied destination SID, but used the
unchecked source SID count to compute the inherited ACE size. That could
advance the temporary inherited ACE buffer pointer and nt_size accounting
past the allocated buffer.

Fix this by validating the parent ACE SID count and SID length before
using the SID during inheritance. Compute the inherited ACE size from the
copied SID so the size matches the bounded destination SID. Reject the
inherited DACL if size accumulation would overflow smb_acl.size or the
security descriptor allocation size.

## References
- https://git.kernel.org/stable/c/1aa60fea7f637c071f529ad6784aecca2f2f0c5f
- https://git.kernel.org/stable/c/47c6e37a77b10e74f70d845ba4ea5d3cafa00336
- https://git.kernel.org/stable/c/996454bc0da84d5a1dedb1a7861823087e01a7ae
- https://git.kernel.org/stable/c/a7fb771314fb3a265d30f8ac245869a367ab065c
- https://git.kernel.org/stable/c/c1d95c995d5bcb24b639200a899eda59cb1e6d64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43490.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43490
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
