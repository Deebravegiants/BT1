# [M] CVE-2020-36558

## Summary
Severity: Medium
Advisory: CVE-2020-36558
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-21
Source: https://osv.dev/vulnerability/CVE-2020-36558
Type: osv

## Details
A race condition in the Linux kernel before 5.5.7 involving VT_RESIZEX could lead to a NULL pointer dereference and general protection fault.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6cd1ed50efd88261298577cd92a14f2768eddeeb
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.7
