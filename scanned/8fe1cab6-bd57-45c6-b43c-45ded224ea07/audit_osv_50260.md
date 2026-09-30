# [M] CVE-2020-0431

## Summary
Severity: Medium
Advisory: CVE-2020-0431
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-17
Source: https://osv.dev/vulnerability/CVE-2020-0431
Type: osv

## Details
In kbd_keycode of keyboard.c, there is a possible out of bounds write due to a missing bounds check. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-144161459

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html
- https://source.android.com/security/bulletin/pixel/2020-09-01
