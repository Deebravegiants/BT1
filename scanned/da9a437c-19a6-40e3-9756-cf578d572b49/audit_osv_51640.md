# [M] CVE-2021-3736

## Summary
Severity: Medium
Advisory: CVE-2021-3736
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3736
Type: osv

## Details
A flaw was found in the Linux kernel. A memory leak problem was found in mbochs_ioctl in samples/vfio-mdev/mbochs.c in Virtual Function I/O (VFIO) Mediated devices. This flaw could allow a local attacker to leak internal kernel information.

## References
- https://access.redhat.com/security/cve/CVE-2021-3736
- https://bugzilla.redhat.com/show_bug.cgi?id=1995570
- https://github.com/torvalds/linux/commit/de5494af4815a4c9328536c72741229b7de88e7f
