# [H] fs/ntfs3: validate rec->used in journal-replay file record check

## Summary
Severity: High
Advisory: CVE-2026-31716
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31716
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.84, >=6.13.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: validate rec->used in journal-replay file record check

check_file_record() validates rec->total against the record size but
never validates rec->used.  The do_action() journal-replay handlers read
rec->used from disk and use it to compute memmove lengths:

  DeleteAttribute:    memmove(attr, ..., used - asize - roff)
  CreateAttribute:    memmove(..., attr, used - roff)
  change_attr_size:   memmove(..., used - PtrOffset(rec, next))

When rec->used is smaller than the offset of a validated attribute, or
larger than the record size, these subtractions can underflow allowing
us to copy huge amounts of memory in to a 4kb buffer, generally
considered a bad idea overall.

This requires a corrupted filesystem, which isn't a threat model the
kernel really needs to worry about, but checking for such an obvious
out-of-bounds value is good to keep things robust, especially on journal
replay

Fix this up by bounding rec->used correctly.

This is much like commit b2bc7c44ed17 ("fs/ntfs3: Fix slab-out-of-bounds
read in DeleteIndexEntryRoot") which checked different values in this
same switch statement.

## References
- https://git.kernel.org/stable/c/0112e6279420d4005b3d57af36fb45c01b8d0116
- https://git.kernel.org/stable/c/0ca0485e4b2e837ebb6cbd4f2451aba665a03e4b
- https://git.kernel.org/stable/c/1393a467a9607e62123806de7d4c3a3e54e396a9
- https://git.kernel.org/stable/c/4b1613d7e2deda831a97e427d1ea586e50fe1be5
- https://git.kernel.org/stable/c/8e64d33198b5a0fb14a452708bad844f94f03b2c
- https://git.kernel.org/stable/c/f79d0403ea20a81bc29105bba54fbcab54e8c403
- https://git.kernel.org/stable/c/f90b8a1798b750755a9e9aee66678f0a1820bbaf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31716.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31716
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
