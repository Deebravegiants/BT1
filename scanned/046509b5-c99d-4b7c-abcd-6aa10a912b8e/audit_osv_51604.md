# [H] CVE-2021-3501

## Summary
Severity: High
Advisory: CVE-2021-3501
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-3501
Type: osv

## Details
A flaw was found in the Linux kernel in versions before 5.12. The value of internal.ndata, in the KVM API, is mapped to an array index, which can be updated by a user process at anytime which could lead to an out-of-bounds write. The highest threat from this vulnerability is to data integrity and system availability.

## References
- https://security.netapp.com/advisory/ntap-20210618-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=1950136
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=04c4f2ee3f68c9a4bf1653d15f1a9a435ae33f7a
