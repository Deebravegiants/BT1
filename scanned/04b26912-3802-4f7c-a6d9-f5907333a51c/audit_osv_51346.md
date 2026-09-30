# [M] CVE-2021-28972

## Summary
Severity: Medium
Advisory: CVE-2021-28972
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-22
Source: https://osv.dev/vulnerability/CVE-2021-28972
Type: osv

## Details
In drivers/pci/hotplug/rpadlpar_sysfs.c in the Linux kernel through 5.11.8, the RPA PCI Hotplug driver has a user-tolerable buffer overflow when writing a new device name to the driver from userspace, allowing userspace to write data to the kernel stack frame directly. This occurs because add_slot_store and remove_slot_store mishandle drc_name '\0' termination, aka CID-cc7a0bb058b8.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4VCKIOXCOZGXBEZMO5LGGV5MWCHO6FT3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PTRNPQTZ4GVS46SZ4OBXY5YDOGVPSTGQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T2S3I4SLRNRUQDOFYUS6IUAZMQNMPNLG/
- https://security.netapp.com/advisory/ntap-20210430-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=cc7a0bb058b85ea03db87169c60c7cfdd5d34678
