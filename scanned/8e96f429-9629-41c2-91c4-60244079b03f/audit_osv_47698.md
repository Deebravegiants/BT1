# [M] CVE-2017-1000255

## Summary
Severity: Medium
Advisory: CVE-2017-1000255
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-10-30
Source: https://osv.dev/vulnerability/CVE-2017-1000255
Type: osv

## Details
On Linux running on PowerPC hardware (Power8 or later) a user process can craft a signal frame and then do a sigreturn so that the kernel will take an exception (interrupt), and use the r1 value *from the signal frame* as the kernel stack pointer. As part of the exception entry the content of the signal frame is written to the kernel stack, allowing an attacker to overwrite arbitrary locations with arbitrary values. The exception handling does produce an oops, and a panic if panic_on_oops=1, but only after kernel memory has been over written. This flaw was introduced in commit: "5d176f751ee3 (powerpc: tm: Enable transactional memory (TM) lazily for userspace)" which was merged upstream into v4.9-rc1. Please note that kernels built with CONFIG_PPC_TRANSACTIONAL_MEM=n are not vulnerable.

## References
- http://www.securityfocus.com/bid/101264
- https://access.redhat.com/errata/RHSA-2018:0654
- https://access.redhat.com/security/cve/CVE-2017-1000255
- https://access.redhat.com/security/cve/CVE-2017-1000255
