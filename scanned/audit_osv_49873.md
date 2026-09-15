# [H] CVE-2019-2025

## Summary
Severity: High
Advisory: CVE-2019-2025
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-2025
Type: osv

## Details
In binder_thread_read of binder.c, there is a possible use-after-free due to improper locking. This could lead to local escalation of privilege in the kernel with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-116855682References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2019-03-01
