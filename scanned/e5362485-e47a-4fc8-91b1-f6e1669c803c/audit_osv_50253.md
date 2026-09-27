# [M] CVE-2020-0305

## Summary
Severity: Medium
Advisory: CVE-2020-0305
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-17
Source: https://osv.dev/vulnerability/CVE-2020-0305
Type: osv

## Details
In cdev_get of char_dev.c, there is a possible use-after-free due to a race condition. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-10Android ID: A-153467744

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00047.html
- https://source.android.com/security/bulletin/pixel/2020-06-01
