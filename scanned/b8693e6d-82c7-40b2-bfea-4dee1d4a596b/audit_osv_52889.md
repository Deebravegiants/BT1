# [M] CVE-2022-20409

## Summary
Severity: Medium
Advisory: CVE-2022-20409
Aliases: A-238177383, ASB-A-238177383
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-20409
Type: osv

## Details
In io_identity_cow of io_uring.c, there is a possible way to corrupt memory due to a use after free. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-238177383References: Upstream kernel

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=2ee0cab11f6626071f8a64c7792406dabdd94c8d
- https://source.android.com/security/bulletin/2022-10-01
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=2ee0cab11f6626071f8a64c7792406dabdd94c8d
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=2ee0cab11f6626071f8a64c7792406dabdd94c8d
- https://source.android.com/security/bulletin/2022-10-01
