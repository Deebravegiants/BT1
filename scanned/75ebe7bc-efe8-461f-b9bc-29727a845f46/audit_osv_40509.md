# [H] ksmbd: fix out-of-bounds read in smb_check_perm_dacl()

## Summary
Severity: High
Advisory: CVE-2026-53390
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53390
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.212, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix out-of-bounds read in smb_check_perm_dacl()

The permission-check ACE walk in smb_check_perm_dacl() validates the ACE
header size and caps sid.num_subauth at SID_MAX_SUB_AUTHORITIES, but it
never checks that ace->size is actually large enough to contain
num_subauth sub-authorities before compare_sids() dereferences them.

CIFS_SID_BASE_SIZE covers the SID header up to but excluding the
sub_auth[] array, and offsetof(struct smb_ace, sid) is the ACE header,
so the existing guards only guarantee the 8-byte SID base, i.e. zero
sub-authorities. compare_sids() then reads ace->sid.sub_auth[i] for
i < min(local_sid->num_subauth, ace->sid.num_subauth). The local
comparison SIDs (sid_everyone, sid_unix_NFS_mode, and the id_to_sid()
result) always have at least one sub-authority, and an attacker controls
the ACE revision and authority bytes (which lie within the in-bounds SID
base), so they can match one of those SIDs and force the sub_auth read.

A crafted ACE with size == 16 and num_subauth >= 1 placed at the tail of
the security descriptor therefore causes a heap out-of-bounds read of up
to SID_MAX_SUB_AUTHORITIES * sizeof(__le32) bytes past the pntsd
allocation. The security descriptor is loaded by ksmbd_vfs_get_sd_xattr()
into a buffer sized exactly to the on-disk data (kzalloc(sd_size) in
ndr_decode_v4_ntacl()), so the read lands past the allocation. The
malformed descriptor can be stored verbatim via SMB2_SET_INFO (the DACL
is not normalised before being written to the security.NTACL xattr) and
the read fires on a subsequent SMB2_CREATE access check, making this
reachable by an authenticated client on a share that uses ACL xattrs.

Add the missing num_subauth-versus-ace_size check, mirroring the
identical guards already present in the sibling parsers parse_dacl() and
smb_inherit_dacl().

## References
- https://git.kernel.org/stable/c/1ef06004ed4bd6d3ed8c840d9d1a376b66d4935b
- https://git.kernel.org/stable/c/36599894fa8536fefdf1e296c0af71b8b7226859
- https://git.kernel.org/stable/c/7627ff8c4f9919f14de562b0160ab4ec9d80b1f7
- https://git.kernel.org/stable/c/988c93d3bba066d8669143e6ec30bb2be9608d53
- https://git.kernel.org/stable/c/c7488c85fd822959e9b5c22fbd9e7c8a21caf5e0
- https://git.kernel.org/stable/c/d5c81a095c86fe507c032d08f3a8cfc518444927
- https://git.kernel.org/stable/c/e36e35660adb9b8ef1435ac359151dda5f094c55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53390.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53390
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
