# [H] ksmbd: reject undersized DACLs before parsing ACEs

## Summary
Severity: High
Advisory: CVE-2026-72382
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72382
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: reject undersized DACLs before parsing ACEs

parse_dacl() limits the attacker-controlled ACE count by comparing it
with the number of minimal ACEs that fit in the DACL size. The DACL size
field is 16 bits, but the expression subtracts sizeof(struct smb_acl).
Because sizeof() is unsigned, a DACL size smaller than the ACL header
underflows to a large size_t.

A malicious client can reach this with:

SMB2_SET_INFO (InfoType=SMB2_O_INFO_SECURITY)
  -> smb2_set_info_sec()
  -> set_info_sec()
  -> parse_sec_desc()
  -> parse_dacl()
     -> init_acl_state(..., 0xffff)
     -> init_acl_state(..., 0xffff)
     -> kmalloc_objs(..., 0xffff)

Thus a malformed security descriptor can make num_aces pass the guard
and drive large temporary ACL state and pointer-array allocations.

Reject DACLs smaller than struct smb_acl before doing the subtraction,
so the ACE count check cannot be bypassed by the underflow.

## References
- https://git.kernel.org/stable/c/15a9e9b8f7f5d7f380ae54c6f5bcbc0bdcb0f3cd
- https://git.kernel.org/stable/c/16fb65ec15fe7c90f50a2115854bfd9a032d4023
- https://git.kernel.org/stable/c/282847c0cf22f2e961155ac8e42f6eeab7e16049
- https://git.kernel.org/stable/c/60908f7ebcd9b6cde74ad5711fab0f49c7970949
- https://git.kernel.org/stable/c/d020e7f27bf65eecd3805404702f716b2b6d9e73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72382.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72382
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
