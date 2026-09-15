# [M] CVE-2021-0561

## Summary
Severity: Medium
Advisory: CVE-2021-0561
Aliases: A-174302683, PUB-A-174302683
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-22
Source: https://osv.dev/vulnerability/CVE-2021-0561
Type: osv

## Details
In append_to_verify_fifo_interleaved_ of stream_encoder.c, there is a possible out of bounds write due to a missing bounds check. This could lead to local information disclosure with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-11Android ID: A-174302683

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EWXBVMPPSL377I7YM55ZYXVKVMYOKES2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q4Y7BW35TGNFYBYBSBDSGLUJHHTYEUSG/
- https://lists.debian.org/debian-lts-announce/2022/03/msg00022.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00003.html
- https://source.android.com/security/bulletin/pixel/2021-06-01
