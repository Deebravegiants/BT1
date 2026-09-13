# [M] CVE-2020-0009

## Summary
Severity: Medium
Advisory: CVE-2020-0009
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2020-0009
Type: osv

## Details
In calc_vm_may_flags of ashmem.c, there is a possible arbitrary write to shared memory due to a permissions bypass. This could lead to local escalation of privilege by corrupting memory shared between processes, with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android Versions: Android kernel Android ID: A-142938932

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://source.android.com/security/bulletin/2020-01-01
- http://packetstormsecurity.com/files/155903/Android-ashmem-Read-Only-Bypasses.html
