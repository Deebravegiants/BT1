# [H] ntfs: reject non-resident records for resident-only attributes

## Summary
Severity: High
Advisory: CVE-2026-72198
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72198
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.9, >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: reject non-resident records for resident-only attributes

The shared lookup-time attribute validator rejects non-resident
$FILE_NAME and $VOLUME_NAME records because their formats require
resident values and callers handle returned records as resident
attributes. Other resident-only attribute types still pass through the
generic non-resident mapping-pairs checks.

That leaves real resident/non-resident union confusion paths. Inode load
looks up $STANDARD_INFORMATION and then reads data.resident.value_offset
without checking a->non_resident. ntfs_inode_sync_standard_information()
does the same when updating the standard information value.
ntfs_write_volume_flags() also looks up $VOLUME_INFORMATION and reads
data.resident.value_offset directly. $INDEX_ROOT callers in dir.c and
index.c depend on the same lookup contract before consuming the resident
index root value.

Reject non-resident records for all resident-only attribute types in the
shared validator. Keep the existing $FILE_NAME and $VOLUME_NAME behavior,
but factor it through a helper and extend it to
$STANDARD_INFORMATION, $OBJECT_ID, $VOLUME_INFORMATION, $INDEX_ROOT, and
$EA_INFORMATION. For $OBJECT_ID and $EA_INFORMATION this is contract
hardening for resident-only formats; this patch only rejects the
non-resident form and does not add new resident value validation for
those types.

## References
- https://git.kernel.org/stable/c/097cdfd0a55df5af82c9753833f39a8bfadbcfcb
- https://git.kernel.org/stable/c/7ffa8f3d30236e0ab897c30bdb01224ff1fe1c89
- https://git.kernel.org/stable/c/b54c9beb90e570bae17a9c18442aeeaf17165ccb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72198.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72198
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
