# [M] CVE-2021-0935

## Summary
Severity: Medium
Advisory: CVE-2021-0935
Aliases: A-168607263, PUB-A-168607263
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-0935
Type: osv

## Details
In ip6_xmit of ip6_output.c, there is a possible out of bounds write due to a use after free. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-168607263References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2021-10-01
