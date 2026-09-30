# [M] CVE-2022-20567

## Summary
Severity: Medium
Advisory: CVE-2022-20567
Aliases: A-186777253, PUB-A-186777253
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-16
Source: https://osv.dev/vulnerability/CVE-2022-20567
Type: osv

## Details
In pppol2tp_create of l2tp_ppp.c, there is a possible use after free due to a race condition. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-186777253References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2022-12-01
- https://source.android.com/security/bulletin/pixel/2022-12-01
