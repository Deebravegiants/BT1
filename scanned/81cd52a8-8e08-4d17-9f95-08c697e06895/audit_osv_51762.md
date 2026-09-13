# [H] CVE-2021-39685

## Summary
Severity: High
Advisory: CVE-2021-39685
Aliases: A-210292376, ASB-A-210292376
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-39685
Type: osv

## Details
In various setup methods of the USB gadget subsystem, there is a possible out of bounds write due to an incorrect flag check. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-210292376References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2022-03-01
- https://source.android.com/security/bulletin/2022-03-01
