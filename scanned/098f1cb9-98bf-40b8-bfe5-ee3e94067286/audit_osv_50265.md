# [M] CVE-2020-0465

## Summary
Severity: Medium
Advisory: CVE-2020-0465
Aliases: A-160818461, A-162844689, ASB-A-162844689, PUB-A-160818461
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-14
Source: https://osv.dev/vulnerability/CVE-2020-0465
Type: osv

## Details
In various methods of hid-multitouch.c, there is a possible out of bounds write due to a missing bounds check. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-162844689References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2020-12-01
- https://source.android.com/security/bulletin/2020-12-01
