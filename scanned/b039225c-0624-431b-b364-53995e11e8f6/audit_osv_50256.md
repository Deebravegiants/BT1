# [H] CVE-2020-0423

## Summary
Severity: High
Advisory: CVE-2020-0423
Aliases: A-161151868, ASB-A-161151868
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-14
Source: https://osv.dev/vulnerability/CVE-2020-0423
Type: osv

## Details
In binder_release_work of binder.c, there is a possible use-after-free due to improper locking. This could lead to local escalation of privilege in the kernel with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-161151868References: N/A

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://source.android.com/security/bulletin/2020-10-01
