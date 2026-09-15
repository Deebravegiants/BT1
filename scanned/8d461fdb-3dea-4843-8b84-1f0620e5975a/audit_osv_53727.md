# [M] CVE-2023-21264

## Summary
Severity: Medium
Advisory: CVE-2023-21264
Aliases: A-279739439, ASB-A-279739439
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-14
Source: https://osv.dev/vulnerability/CVE-2023-21264
Type: osv

## Details
In multiple functions of mem_protect.c, there is a possible way to access hypervisor memory due to a memory access check in the wrong place. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.

## References
- https://source.android.com/security/bulletin/2023-08-01
- https://android.googlesource.com/kernel/common/+/53625a846a7b4
- https://android.googlesource.com/kernel/common/+/b35a06182451f
- https://source.android.com/security/bulletin/2023-08-01
