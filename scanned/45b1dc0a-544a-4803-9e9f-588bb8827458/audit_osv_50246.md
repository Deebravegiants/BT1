# [M] CVE-2020-0066

## Summary
Severity: Medium
Advisory: CVE-2020-0066
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-10
Source: https://osv.dev/vulnerability/CVE-2020-0066
Type: osv

## Details
In the netlink driver, there is a possible out of bounds write due to a race condition. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-65025077

## References
- https://source.android.com/security/bulletin/pixel/2020-03-01
