# [M] CVE-2019-16229

## Summary
Severity: Medium
Advisory: CVE-2019-16229
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CVE-2019-16229
Type: osv

## Details
drivers/gpu/drm/amd/amdkfd/kfd_interrupt.c in the Linux kernel 5.2.14 does not check the alloc_workqueue return value, leading to a NULL pointer dereference. NOTE: The security community disputes this issues as not being serious enough to be deserving a CVE id

## References
- https://usn.ubuntu.com/4287-1/
- https://usn.ubuntu.com/4287-2/
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://usn.ubuntu.com/4284-1/
- https://usn.ubuntu.com/4285-1/
- https://bugzilla.suse.com/show_bug.cgi?id=1150469#c3
- https://lkml.org/lkml/2019/9/9/487
