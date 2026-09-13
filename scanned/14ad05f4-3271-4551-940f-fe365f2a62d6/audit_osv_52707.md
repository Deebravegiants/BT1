# [M] CVE-2022-0494

## Summary
Severity: Medium
Advisory: CVE-2022-0494
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2022-0494
Type: osv

## Details
A kernel information leak flaw was identified in the scsi_ioctl function in drivers/scsi/scsi_ioctl.c in the Linux kernel. This flaw allows a local attacker with a special user privilege (CAP_SYS_ADMIN or CAP_SYS_RAWIO) to create issues with confidentiality.

## References
- https://lore.kernel.org/all/20220216084038.15635-1-tcs.kernel%40gmail.com/
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://www.debian.org/security/2022/dsa-5161
- https://www.debian.org/security/2022/dsa-5173
- https://bugzilla.redhat.com/show_bug.cgi?id=2039448
