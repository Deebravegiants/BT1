# [H] CVE-2018-9465

## Summary
Severity: High
Advisory: CVE-2018-9465
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-06
Source: https://osv.dev/vulnerability/CVE-2018-9465
Type: osv

## Details
In task_get_unused_fd_flags of binder.c, there is a possible memory corruption due to a use after free. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android Versions: Android kernel Android ID: A-69164715 References: Upstream kernel.

## References
- http://www.securitytracker.com/id/1041432
- https://source.android.com/security/bulletin/2018-08-01
- https://source.android.com/security/bulletin/2018-08-01
