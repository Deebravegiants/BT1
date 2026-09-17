# [H] CVE-2021-39634

## Summary
Severity: High
Advisory: CVE-2021-39634
Aliases: A-204450605, ASB-A-204450605
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2021-39634
Type: osv

## Details
In fs/eventpoll.c, there is a possible use after free. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-204450605References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2022-01-01
- https://source.android.com/security/bulletin/2022-01-01
