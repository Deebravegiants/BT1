# [M] CVE-2025-55095

## Summary
Severity: Medium
Advisory: CVE-2025-55095
Aliases: GHSA-qfmp-wch9-rpv2
CVSS: 4.2 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2025-55095
Type: osv

## Details
The function _ux_host_class_storage_media_mount() is responsible for mounting partitions on a USB mass storage device. When it encounters an extended partition entry in the partition table, it recursively calls itself to mount the next logical partition.

This recursion occurs in _ux_host_class_storage_partition_read(), which parses up to four partition entries. If an extended partition is found (with type UX_HOST_CLASS_STORAGE_PARTITION_EXTENDED or EXTENDED_LBA_MAPPED), the code invokes:
            _ux_host_class_storage_media_mount(storage, sector + _ux_utility_long_get(...));


There is no limit on the recursion depth or tracking of visited sectors. As a result, a malicious or malformed disk image can include cyclic or excessively deep chains of extended partitions, causing the function to recurse until stack overflow occurs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55095.json
- https://github.com/eclipse-threadx/usbx/security/advisories/GHSA-qfmp-wch9-rpv2
- https://nvd.nist.gov/vuln/detail/CVE-2025-55095
- https://github.com/eclipse-threadx/usbx
