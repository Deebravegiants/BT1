# [H] CVE-2018-9415

## Summary
Severity: High
Advisory: CVE-2018-9415
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-06
Source: https://osv.dev/vulnerability/CVE-2018-9415
Type: osv

## Details
In driver_override_store and driver_override_show of bus.c, there is a possible double free due to improper locking. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation. Product: Android Versions: Android kernel Android ID: A-69129004 References: Upstream kernel.

## References
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3752-3/
- https://source.android.com/security/bulletin/pixel/2018-07-01
