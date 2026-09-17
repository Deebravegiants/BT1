# [M] CVE-2019-16230

## Summary
Severity: Medium
Advisory: CVE-2019-16230
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CVE-2019-16230
Type: osv

## Details
drivers/gpu/drm/radeon/radeon_display.c in the Linux kernel 5.2.14 does not check the alloc_workqueue return value, leading to a NULL pointer dereference. NOTE: A third-party software maintainer states that the work queue allocation is happening during device initialization, which for a graphics card occurs during boot. It is not attacker controllable and OOM at that time is highly unlikely

## References
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://bugzilla.suse.com/show_bug.cgi?id=1150468
- https://lkml.org/lkml/2019/9/9/487
