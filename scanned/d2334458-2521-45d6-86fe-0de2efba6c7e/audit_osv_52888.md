# [M] CVE-2022-20369

## Summary
Severity: Medium
Advisory: CVE-2022-20369
Aliases: A-223375145, PUB-A-223375145
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-11
Source: https://osv.dev/vulnerability/CVE-2022-20369
Type: osv

## Details
In v4l2_m2m_querybuf of v4l2-mem2mem.c, there is a possible out of bounds write due to improper input validation. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-223375145References: Upstream kernel

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://source.android.com/security/bulletin/pixel/2022-08-01
