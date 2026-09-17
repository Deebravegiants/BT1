# [H] CVE-2019-2214

## Summary
Severity: High
Advisory: CVE-2019-2214
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-13
Source: https://osv.dev/vulnerability/CVE-2019-2214
Type: osv

## Details
In binder_transaction of binder.c, there is a possible out of bounds write due to a missing bounds check. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-136210786References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2019-11-01
- https://usn.ubuntu.com/4226-1/
- http://packetstormsecurity.com/files/156185/Kernel-Live-Patch-Security-Notice-LSN-0062-1.html
