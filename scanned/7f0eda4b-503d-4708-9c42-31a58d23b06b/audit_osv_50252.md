# [M] CVE-2020-0256

## Summary
Severity: Medium
Advisory: CVE-2020-0256
Aliases: A-152874864, ASB-A-152874864
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-11
Source: https://osv.dev/vulnerability/CVE-2020-0256
Type: osv

## Details
In LoadPartitionTable of gpt.cc, there is a possible out of bounds write due to a missing bounds check. This could lead to local escalation of privilege when inserting a malicious USB device, with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-8.1 Android-9 Android-10 Android-8.0Android ID: A-152874864

## References
- https://lists.debian.org/debian-lts-announce/2021/02/msg00010.html
- https://source.android.com/security/bulletin/2020-08-01
