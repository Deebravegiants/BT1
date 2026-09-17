# [M] CVE-2023-45862

## Summary
Severity: Medium
Advisory: CVE-2023-45862
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-14
Source: https://osv.dev/vulnerability/CVE-2023-45862
Type: osv

## Details
An issue was discovered in drivers/usb/storage/ene_ub6250.c for the ENE UB6250 reader driver in the Linux kernel before 6.2.5. An object could potentially extend beyond the end of an allocation.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.5
- https://security.netapp.com/advisory/ntap-20231116-0004/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ce33e64c1788912976b61314b56935abd4bc97ef
