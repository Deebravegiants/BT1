# [H] CVE-2019-2213

## Summary
Severity: High
Advisory: CVE-2019-2213
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-13
Source: https://osv.dev/vulnerability/CVE-2019-2213
Type: osv

## Details
In binder_free_transaction of binder.c, there is a possible use-after-free due to a race condition. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-133758011References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2019-11-01
