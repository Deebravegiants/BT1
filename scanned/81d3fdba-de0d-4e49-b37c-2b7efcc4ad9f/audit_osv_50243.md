# [H] CVE-2020-0030

## Summary
Severity: High
Advisory: CVE-2020-0030
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-13
Source: https://osv.dev/vulnerability/CVE-2020-0030
Type: osv

## Details
In binder_thread_release of binder.c, there is a possible use after free due to a race condition. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-145286050References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2020-02-01
- https://source.android.com/security/bulletin/2020-02-01
