# [M] CVE-2023-34324

## Summary
Severity: Medium
Advisory: CVE-2023-34324
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/CVE-2023-34324
Type: osv

## Details
Closing of an event channel in the Linux kernel can result in a deadlock.
This happens when the close is being performed in parallel to an unrelated
Xen console action and the handling of a Xen console interrupt in an
unprivileged guest.

The closing of an event channel is e.g. triggered by removal of a
paravirtual device on the other side. As this action will cause console
messages to be issued on the other side quite often, the chance of
triggering the deadlock is not neglectable.

Note that 32-bit Arm-guests are not affected, as the 32-bit Linux kernel
on Arm doesn't use queued-RW-locks, which are required to trigger the
issue (on Arm32 a waiting writer doesn't block further readers to get
the lock).

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- http://xenbits.xen.org/xsa/advisory-441.html
- https://xenbits.xenproject.org/xsa/advisory-441.html
