# [M] CVE-2021-46968

## Summary
Severity: Medium
Advisory: CVE-2021-46968
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46968
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/zcrypt: fix zcard and zqueue hot-unplug memleak

Tests with kvm and a kmemdebug kernel showed, that on hot unplug the
zcard and zqueue structs for the unplugged card or queue are not
properly freed because of a mismatch with get/put for the embedded
kref counter.

This fix now adjusts the handling of the kref counters. With init the
kref counter starts with 1. This initial value needs to drop to zero
with the unregister of the card or queue to trigger the release and
free the object.

## References
- https://git.kernel.org/stable/c/971dc8706cee47393d393905d294ea47e39503d3
- https://git.kernel.org/stable/c/026499a9c2e002e621ad568d1378324ae97e5524
- https://git.kernel.org/stable/c/055a063a18bcd19b93709e3eac8078d6b2f04599
- https://git.kernel.org/stable/c/70fac8088cfad9f3b379c9082832b4d7532c16c2
