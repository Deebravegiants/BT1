# [H] CVE-2018-9568

## Summary
Severity: High
Advisory: CVE-2018-9568
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-9568
Type: osv

## Details
In sk_clone_lock of sock.c, there is a possible memory corruption due to type confusion. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android. Versions: Android kernel. Android ID: A-113509306. References: Upstream kernel.

## References
- https://usn.ubuntu.com/3880-1/
- https://usn.ubuntu.com/3880-2/
- https://access.redhat.com/errata/RHSA-2019:0512
- https://access.redhat.com/errata/RHSA-2019:0514
- https://access.redhat.com/errata/RHSA-2019:2696
- https://access.redhat.com/errata/RHSA-2019:2730
- https://access.redhat.com/errata/RHSA-2019:2736
- https://access.redhat.com/errata/RHSA-2019:4056
- https://access.redhat.com/errata/RHSA-2019:4159
- https://access.redhat.com/errata/RHSA-2019:4164
- https://access.redhat.com/errata/RHSA-2019:3967
- https://access.redhat.com/errata/RHSA-2019:4255
- https://source.android.com/security/bulletin/2018-12-01
