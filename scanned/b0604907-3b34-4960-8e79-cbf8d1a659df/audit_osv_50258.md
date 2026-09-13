# [M] CVE-2020-0429

## Summary
Severity: Medium
Advisory: CVE-2020-0429
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-17
Source: https://osv.dev/vulnerability/CVE-2020-0429
Type: osv

## Details
In l2tp_session_delete and related functions of l2tp_core.c, there is possible memory corruption due to a use after free. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-152735806

## References
- https://source.android.com/security/bulletin/pixel/2020-09-01
- https://source.android.com/security/bulletin/pixel/2020-09-01
