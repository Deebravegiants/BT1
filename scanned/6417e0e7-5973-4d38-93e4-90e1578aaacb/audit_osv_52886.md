# [M] CVE-2022-20154

## Summary
Severity: Medium
Advisory: CVE-2022-20154
Aliases: A-174846563, PUB-A-174846563
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-15
Source: https://osv.dev/vulnerability/CVE-2022-20154
Type: osv

## Details
In lock_sock_nested of sock.c, there is a possible use after free due to a race condition. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-174846563References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2022-06-01
