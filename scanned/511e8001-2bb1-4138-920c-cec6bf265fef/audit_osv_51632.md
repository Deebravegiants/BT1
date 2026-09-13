# [M] CVE-2021-3659

## Summary
Severity: Medium
Advisory: CVE-2021-3659
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2021-3659
Type: osv

## Details
A NULL pointer dereference flaw was found in the Linux kernel’s IEEE 802.15.4 wireless networking subsystem in the way the user closes the LR-WPAN connection. This flaw allows a local user to crash the system. The highest threat from this vulnerability is to system availability.

## References
- https://access.redhat.com/security/cve/CVE-2021-3659
- https://bugzilla.redhat.com/show_bug.cgi?id=1975949
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=1165affd484889d4986cf3b724318935a0b120d8
