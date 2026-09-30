# [H] CVE-2022-20421

## Summary
Severity: High
Advisory: CVE-2022-20421
Aliases: A-239630375, ASB-A-239630375
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-20421
Type: osv

## Details
In binder_inc_ref_for_node of binder.c, there is a possible way to corrupt memory due to a use after free. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-239630375References: Upstream kernel

## References
- https://www.debian.org/security/2022/dsa-5257
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://source.android.com/security/bulletin/2022-10-01
