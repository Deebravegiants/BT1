# [H] CVE-2019-10142

## Summary
Severity: High
Advisory: CVE-2019-10142
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-10142
Type: osv

## Details
A flaw was found in the Linux kernel's freescale hypervisor manager implementation, kernel versions 5.0.x up to, excluding 5.0.17. A parameter passed to an ioctl was incorrectly validated and used in size calculations for the page size calculation. An attacker can use this flaw to crash the system, corrupt memory, or create other adverse security affects.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10142
