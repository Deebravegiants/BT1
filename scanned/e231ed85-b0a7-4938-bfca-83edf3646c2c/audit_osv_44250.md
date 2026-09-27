# [C] ntfs: bound the look-ahead attribute-list entry in ntfs_external_attr_find()

## Summary
Severity: Critical
Advisory: CVE-2026-80673
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80673
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: bound the look-ahead attribute-list entry in ntfs_external_attr_find()

When resolving an attribute lookup with a non-zero @lowest_vcn,
ntfs_external_attr_find() peeks at the next $ATTRIBUTE_LIST entry to
decide whether to keep searching, but bounds that not-yet-validated
entry only with "(u8 *)next_al_entry + 6 < al_end" (which proves just
bytes 0..6 are in range) and "(u8 *)next_al_entry + length <= al_end"
with an attacker-controlled, non-8-aligned length. It then reads
next_al_entry->lowest_vcn (an __le64 at offset 8) and the name at
next_al_entry->name_offset, both of which can lie past al_end -- the
exact end of the kvmalloc'd attribute-list buffer (allocated at the
on-disk attr_list_size, no rounding). A crafted on-disk $ATTRIBUTE_LIST
whose last entry sits a few bytes before al_end therefore yields a slab
out-of-bounds read when the inode is read.

Validate the look-ahead entry with ntfs_attr_list_entry_is_valid() (added
in patch 1/3) before dereferencing lowest_vcn and the name, so the same
fixed-header, length and name bounds the main attribute-list walk uses now
guard this read too.

## References
- https://git.kernel.org/stable/c/344b18f389f9934d59c7b0cf3d20541ea2e0da58
- https://git.kernel.org/stable/c/44885c9b45eb4082fb7f558590d84bb254a08e94
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80673.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80673
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
