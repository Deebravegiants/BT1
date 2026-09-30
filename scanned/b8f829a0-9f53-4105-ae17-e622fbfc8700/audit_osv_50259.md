# [H] CVE-2020-0430

## Summary
Severity: High
Advisory: CVE-2020-0430
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-17
Source: https://osv.dev/vulnerability/CVE-2020-0430
Type: osv

## Details
In skb_headlen of /include/linux/skbuff.h, there is a possible out of bounds read due to memory corruption. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-153881554

## References
- https://source.android.com/security/bulletin/pixel/2020-09-01
