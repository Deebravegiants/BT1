# [M] CVE-2021-39656

## Summary
Severity: Medium
Advisory: CVE-2021-39656
Aliases: A-174049066, PUB-A-174049066
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-39656
Type: osv

## Details
In __configfs_open_file of file.c, there is a possible use-after-free due to improper locking. This could lead to local escalation of privilege in the kernel with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-174049066References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2021-12-01
- https://source.android.com/security/bulletin/pixel/2021-12-01
