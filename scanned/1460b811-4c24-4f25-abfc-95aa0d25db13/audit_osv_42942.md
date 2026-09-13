# [C] ntfs: validate resident index root values on lookup

## Summary
Severity: Critical
Advisory: CVE-2026-72199
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72199
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: validate resident index root values on lookup

Resident $INDEX_ROOT values carry index header fields that callers
consume after lookup. Some callers already validate parts of the layout
before walking entries, but those checks are scattered and do not cover
all root header invariants, such as entries_offset alignment and lower
bound, index_length, and allocated_size consistency.

The resident root resize paths now keep these header fields consistent
while the value size changes: ntfs_ir_truncate() lowers
index.allocated_size before shrinking the resident value, and
ntfs_ir_reparent() grows the resident value before publishing a larger
root header. Lookup-time validation can therefore cover these invariants
without tripping over the driver's own resize paths.

Add $INDEX_ROOT to the minimum resident value size table and validate the
resident index header fields before returning the attribute from lookup.
Require 8-byte aligned index header fields, a sane entries_offset, an
index_length within allocated_size, allocated_size within the resident
value, and enough entry space for at least an index entry header.

The shared validator already rejects non-resident records for
resident-only attribute types, including $INDEX_ROOT.

## References
- https://git.kernel.org/stable/c/bfb01dd319b6b4c3e79756de7b75ccf0b9a0a247
- https://git.kernel.org/stable/c/fcf5bf0e8570798970e3ae8c95d04765ba2c5b97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72199.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72199
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
