# [H] ksmbd: validate num_subauth when copying ACE in set_ntacl_dacl

## Summary
Severity: High
Advisory: CVE-2026-68100
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68100
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate num_subauth when copying ACE in set_ntacl_dacl

set_ntacl_dacl() copies each ACE from the attacker-controlled stored
security descriptor verbatim into the response DACL without checking
sid.num_subauth. The ACE bytes (including an unchecked num_subauth)
originate from an authenticated SMB2_SET_INFO(SecInfo=DACL) that is
stored raw via ksmbd_vfs_set_sd_xattr(); parse_dacl() rejects a bad ACE
with `break` rather than an error, so parse_sec_desc() still returns
success and the malformed SD reaches the xattr intact.

On a subsequent SMB2_QUERY_INFO(SecInfo=DACL) for an inode carrying a
POSIX access ACL, build_sec_desc() -> set_ntacl_dacl() ->
set_posix_acl_entries_dacl() walks the copied ACEs and reads

    ntace->sid.sub_auth[ntace->sid.num_subauth - 1]

with num_subauth taken straight from the stored SD. Since sub_auth[]
is fixed at SID_MAX_SUB_AUTHORITIES (15), a crafted num_subauth (e.g.
255) drives an out-of-bounds heap read of ~1 KB with an offset fully
controlled by an authenticated client.

The sibling functions already gate this field:
  parse_dacl()    -- num_subauth == 0 || > SID_MAX_SUB_AUTHORITIES
  parse_sid()     -- num_subauth > SID_MAX_SUB_AUTHORITIES
  smb_copy_sid()  -- min_t(u8, num_subauth, SID_MAX_SUB_AUTHORITIES)
set_ntacl_dacl() is the lone inconsistent path that omits the check.

Add the same num_subauth validation in set_ntacl_dacl() before copying
the ACE, matching the gate already enforced by parse_dacl().

## References
- https://git.kernel.org/stable/c/26cb845e22a00c85bf566337417fa33492395f10
- https://git.kernel.org/stable/c/47f0b34f6bc98ed85bfdc293e8f3e432ec24958d
- https://git.kernel.org/stable/c/5acbd3012fd4a7ccfebd91ea6f784120084eb897
- https://git.kernel.org/stable/c/b6d3cc6a524416dfdb2b47e4bba2e7e20011d056
- https://git.kernel.org/stable/c/e31fada5143784bc05c7ae44c79eed9b7a2e147e
- https://git.kernel.org/stable/c/fb3dc8e6da46a1ccad1956cda57de29d9b3033e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68100.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68100
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
