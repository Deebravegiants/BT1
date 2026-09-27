# [H] CVE-2019-2181

## Summary
Severity: High
Advisory: CVE-2019-2181
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-09-05
Source: https://osv.dev/vulnerability/CVE-2019-2181
Type: osv

## Details
In binder_transaction of binder.c in the Android kernel, there is a possible out of bounds write due to an integer overflow. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is needed for exploitation.

## References
- https://source.android.com/security/bulletin/2019-09-01
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://usn.ubuntu.com/4157-1/
- https://usn.ubuntu.com/4157-2/
