# [M] CVE-2020-0067

## Summary
Severity: Medium
Advisory: CVE-2020-0067
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-17
Source: https://osv.dev/vulnerability/CVE-2020-0067
Type: osv

## Details
In f2fs_xattr_generic_list of xattr.c, there is a possible out of bounds read due to a missing bounds check. This could lead to local information disclosure with System execution privileges needed. User interaction is not required for exploitation.Product: Android. Versions: Android kernel. Android ID: A-120551147.

## References
- https://source.android.com/security/bulletin/pixel/2020-04-01
- https://usn.ubuntu.com/4387-1/
- https://usn.ubuntu.com/4388-1/
- https://usn.ubuntu.com/4389-1/
- https://usn.ubuntu.com/4390-1/
- https://usn.ubuntu.com/4527-1/
- http://android.googlesource.com/kernel/common/+/688078e7
- http://packetstormsecurity.com/files/159565/Kernel-Live-Patch-Security-Notice-LSN-0072-1.html
