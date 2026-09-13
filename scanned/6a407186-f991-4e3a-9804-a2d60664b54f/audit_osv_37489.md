# [H] ksmbd: validate num_aces and harden ACE walk in smb_inherit_dacl()

## Summary
Severity: High
Advisory: CVE-2026-31706
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31706
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.12.84, >=6.13.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate num_aces and harden ACE walk in smb_inherit_dacl()

smb_inherit_dacl() trusts the on-disk num_aces value from the parent
directory's DACL xattr and uses it to size a heap allocation:

  aces_base = kmalloc(sizeof(struct smb_ace) * num_aces * 2, ...);

num_aces is a u16 read from le16_to_cpu(parent_pdacl->num_aces)
without checking that it is consistent with the declared pdacl_size.
An authenticated client whose parent directory's security.NTACL is
tampered (e.g. via offline xattr corruption or a concurrent path that
bypasses parse_dacl()) can present num_aces = 65535 with minimal
actual ACE data.  This causes a ~8 MB allocation (not kzalloc, so
uninitialized) that the subsequent loop only partially populates, and
may also overflow the three-way size_t multiply on 32-bit kernels.

Additionally, the ACE walk loop uses the weaker
offsetof(struct smb_ace, access_req) minimum size check rather than
the minimum valid on-wire ACE size, and does not reject ACEs whose
declared size is below the minimum.

Reproduced on UML + KASAN + LOCKDEP against the real ksmbd code path.
A legitimate mount.cifs client creates a parent directory over SMB
(ksmbd writes a valid security.NTACL xattr), then the NTACL blob on
the backing filesystem is rewritten to set num_aces = 0xFFFF while
keeping the posix_acl_hash bytes intact so ksmbd_vfs_get_sd_xattr()'s
hash check still passes.  A subsequent SMB2 CREATE of a child under
that parent drives smb2_open() into smb_inherit_dacl() (share has
"vfs objects = acl_xattr" set), which fails the page allocator:

  WARNING: mm/page_alloc.c:5226 at __alloc_frozen_pages_noprof+0x46c/0x9c0
  Workqueue: ksmbd-io handle_ksmbd_work
   __alloc_frozen_pages_noprof+0x46c/0x9c0
   ___kmalloc_large_node+0x68/0x130
   __kmalloc_large_node_noprof+0x24/0x70
   __kmalloc_noprof+0x4c9/0x690
   smb_inherit_dacl+0x394/0x2430
   smb2_open+0x595d/0xabe0
   handle_ksmbd_work+0x3d3/0x1140

With the patch applied the added guard rejects the tampered value
with -EINVAL before any large allocation runs, smb2_open() falls back
to smb2_create_sd_buffer(), and the child is created with a default
SD.  No warning, no splat.

Fix by:

  1. Validating num_aces against pdacl_size using the same formula
     applied in parse_dacl().

  2. Replacing the raw kmalloc(sizeof * num_aces * 2) with
     kmalloc_array(num_aces * 2, sizeof(...)) for overflow-safe
     allocation.

  3. Tightening the per-ACE loop guard to require the minimum valid
     ACE size (offsetof(smb_ace, sid) + CIFS_SID_BASE_SIZE) and
     rejecting under-sized ACEs, matching the hardening in
     smb_check_perm_dacl() and parse_dacl().

v1 -> v2:
  - Replace the synthetic test-module splat in the changelog with a
    real-path UML + KASAN reproduction driven through mount.cifs and
    SMB2 CREATE; Namjae flagged the kcifs3_test_inherit_dacl_old name
    in v1 since it does not exist in ksmbd.
  - Drop the commit-hash citation from the code comment per Namjae's
    review; keep the parse_dacl() pointer.

## References
- https://git.kernel.org/stable/c/063a7409b0de46d7c770b65bb0338e6fdb3b1f0a
- https://git.kernel.org/stable/c/3e4e2ea2a781018ed5d75f969e3e5606beb66e48
- https://git.kernel.org/stable/c/3e5360b422dd741cb315654a191fa73869a37414
- https://git.kernel.org/stable/c/59c32abaaec9cdd6164811c7e864e72f7554b82d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31706.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31706
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
