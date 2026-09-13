# [H] scsi: mpi3mr: Fix corrupt config pages PHY state is switched in sysfs

## Summary
Severity: High
Advisory: CVE-2024-57804
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57804
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpi3mr: Fix corrupt config pages PHY state is switched in sysfs

The driver, through the SAS transport, exposes a sysfs interface to
enable/disable PHYs in a controller/expander setup.  When multiple PHYs
are disabled and enabled in rapid succession, the persistent and current
config pages related to SAS IO unit/SAS Expander pages could get
corrupted.

Use separate memory for each config request.

## References
- https://git.kernel.org/stable/c/711201a8b8334a397440ac0b859df0054e174bc9
- https://git.kernel.org/stable/c/869fdc6f0606060301aef648231e186c7c542f5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57804.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57804
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
