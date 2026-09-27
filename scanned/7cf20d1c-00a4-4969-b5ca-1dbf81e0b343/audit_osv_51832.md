# [H] CVE-2021-4157

## Summary
Severity: High
Advisory: CVE-2021-4157
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-4157
Type: osv

## Details
An out of memory bounds write flaw (1 or 2 bytes of memory) in the Linux kernel NFS subsystem was found in the way users use mirroring (replication of files with NFS). A user, having access to the NFS mount, could potentially use this flaw to crash the system or escalate privileges on the system.

## References
- https://lore.kernel.org/lkml/20210517140244.822185482%40linuxfoundation.org/
- https://security.netapp.com/advisory/ntap-20220602-0007/
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2034342
