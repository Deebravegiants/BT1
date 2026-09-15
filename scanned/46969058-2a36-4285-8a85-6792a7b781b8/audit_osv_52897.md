# [M] CVE-2022-2085

## Summary
Severity: Medium
Advisory: CVE-2022-2085
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-16
Source: https://osv.dev/vulnerability/CVE-2022-2085
Type: osv

## Details
A NULL pointer dereference vulnerability was found in Ghostscript, which occurs when it tries to render a large number of bits in memory. When allocating a buffer device, it relies on an init_device_procs defined for the device that uses it as a prototype that depends upon the number of bits per pixel. For bpp > 64, mem_x_device is used and does not have an init_device_procs defined. This flaw allows an attacker to parse a large number of bits (more than 64 bits per pixel), which triggers a NULL pointer dereference flaw, causing an application to crash.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Bh=ae1061d948d88667bdf51d47d918c4684d0f67df
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ERSZX5LKDWAHZWJYBMP2E2UHOPUCDEGV/
- https://security.gentoo.org/glsa/202211-11
- https://security.gentoo.org/glsa/202309-03
- https://bugs.ghostscript.com/show_bug.cgi?id=704945
- https://bugzilla.redhat.com/show_bug.cgi?id=2095261
