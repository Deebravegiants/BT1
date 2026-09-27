# [H] CVE-2022-20422

## Summary
Severity: High
Advisory: CVE-2022-20422
Aliases: A-237540956, ASB-A-237540956
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-20422
Type: osv

## Details
In emulation_proc_handler of armv8_deprecated.c, there is a possible way to corrupt memory due to a race condition. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-237540956References: Upstream kernel

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://source.android.com/security/bulletin/2022-10-01
