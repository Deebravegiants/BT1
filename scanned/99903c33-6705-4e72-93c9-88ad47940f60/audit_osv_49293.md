# [M] CVE-2018-9517

## Summary
Severity: Medium
Advisory: CVE-2018-9517
CVSS: 6.7 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-9517
Type: osv

## Details
In pppol2tp_connect, there is possible memory corruption due to a use after free. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation. Product: Android. Versions: Android kernel. Android ID: A-38159931.

## References
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://source.android.com/security/bulletin/pixel/2018-09-01
- https://source.android.com/security/bulletin/pixel/2018-09-01
- https://usn.ubuntu.com/3932-1/
- https://usn.ubuntu.com/3932-2/
