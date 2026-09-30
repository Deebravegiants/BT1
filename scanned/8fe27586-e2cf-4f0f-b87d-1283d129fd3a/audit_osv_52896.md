# [M] CVE-2022-20572

## Summary
Severity: Medium
Advisory: CVE-2022-20572
Aliases: A-234475629, PUB-A-234475629
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-16
Source: https://osv.dev/vulnerability/CVE-2022-20572
Type: osv

## Details
In verity_target of dm-verity-target.c, there is a possible way to modify read-only files due to a missing permission check. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-234475629References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2022-12-01
- https://source.android.com/security/bulletin/pixel/2022-12-01
