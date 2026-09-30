# [H] CVE-2021-39698

## Summary
Severity: High
Advisory: CVE-2021-39698
Aliases: A-185125206, ASB-A-185125206
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-39698
Type: osv

## Details
In aio_poll_complete_work of aio.c, there is a possible memory corruption due to a use after free. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-185125206References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2022-03-01
- https://source.android.com/security/bulletin/2022-03-01
