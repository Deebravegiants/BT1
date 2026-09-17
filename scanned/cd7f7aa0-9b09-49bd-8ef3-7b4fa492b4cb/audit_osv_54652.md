# [M] CVE-2024-24855

## Summary
Severity: Medium
Advisory: CVE-2024-24855
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-24855
Type: osv

## Details
A race condition was found in the Linux kernel's scsi device driver in lpfc_unregister_fcf_rescan() function. This can result in a null pointer dereference issue, possibly leading to a kernel panic or denial of service issue.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://bugzilla.openanolis.cn/show_bug.cgi?id=8149
