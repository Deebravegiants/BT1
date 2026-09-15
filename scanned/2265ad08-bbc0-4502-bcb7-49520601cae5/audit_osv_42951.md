# [C] ntfs: validate attribute values on lookup

## Summary
Severity: Critical
Advisory: CVE-2026-72209
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72209
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: validate attribute values on lookup

ntfs_attr_find() and ntfs_external_attr_find() check that generic
resident attribute values fit in their attribute records and that
fixed-size resident values are large enough. For variable-length resident
formats, however, the fixed part is not enough: embedded length fields
can still point callers past the resident value.

A crafted image can set a small resident $FILE_NAME value_length while
leaving file_name_length large. Callers then trust file_name_length and
read past the resident value when converting or comparing the name. This
was reproduced with a crafted image under KASAN as a slab-out-of-bounds
read from the kmalloc-1k MFT record copy. The stack included
ntfs_lookup(), ntfs_iget(), ntfs_read_locked_inode(), ntfs_attr_name_get(),
ntfs_ucstonls(), and utf16s_to_utf8s().

Add a shared attribute value validator and use it before a lookup path
can return an attribute, including the AT_UNUSED enumeration case where
callers inspect returned attributes directly. The helper validates
resident value bounds, minimum resident value sizes, variable-length
$FILE_NAME fields, and non-resident mapping-pairs metadata that was
previously checked separately in both lookup paths.

This also preserves the intended resident @val matching semantics in the
external attribute lookup path. The old duplicated validation block
overwrote the actual resident value length with the type-specific minimum
length before comparing @val, so variable-length resident values could
fail to match even when the bytes were identical. Keep the comparison on
the actual value length, and make ntfs_attrlist_entry_add() compare
resident attributes with lowest_vcn zero instead of reading the
non-resident union member after a successful resident match.

Reject non-resident $FILE_NAME records too: the format requires
$FILE_NAME to be resident and callers treat returned records as resident.

## References
- https://git.kernel.org/stable/c/d5803e3345dae9c6470bb61869885236276b9a35
- https://git.kernel.org/stable/c/e4c36dfac57a7261e9aeb0f3a7f30944a8aefb56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72209.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72209
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
