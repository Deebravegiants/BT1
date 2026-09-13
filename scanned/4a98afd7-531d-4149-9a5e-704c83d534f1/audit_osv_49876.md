# [H] CVE-2019-2054

## Summary
Severity: High
Advisory: CVE-2019-2054
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-08
Source: https://osv.dev/vulnerability/CVE-2019-2054
Type: osv

## Details
In the seccomp implementation prior to kernel version 4.8, there is a possible seccomp bypass due to seccomp policies that allow the use of ptrace. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android Versions: Android kernel Android ID: A-119769499

## References
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://source.android.com/security/bulletin/2019-05-01
- https://usn.ubuntu.com/4076-1/
- https://usn.ubuntu.com/4095-2/
- http://packetstormsecurity.com/files/153799/Kernel-Live-Patch-Security-Notice-LSN-0053-1.html
