# [M] CVE-2023-2513

## Summary
Severity: Medium
Advisory: CVE-2023-2513
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-08
Source: https://osv.dev/vulnerability/CVE-2023-2513
Type: osv

## Details
A use-after-free vulnerability was found in the Linux kernel's ext4 filesystem in the way it handled the extra inode size for extended attributes. This flaw could allow a privileged local user to cause a system crash or other undefined behaviors.

## References
- https://lore.kernel.org/all/20220616021358.2504451-1-libaokun1%40huawei.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2513.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2513
- https://bugzilla.redhat.com/show_bug.cgi?id=2193097
- https://github.com/torvalds/linux/commit/67d7d8ad99be
