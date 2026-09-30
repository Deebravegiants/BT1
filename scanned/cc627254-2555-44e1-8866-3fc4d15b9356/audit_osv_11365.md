# [H] CVE-2017-7539

## Summary
Severity: High
Advisory: CVE-2017-7539
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2017-7539
Type: osv

## Details
An assertion-failure flaw was found in Qemu before 2.10.1, in the Network Block Device (NBD) server's initial connection negotiation, where the I/O coroutine was undefined. This could crash the qemu-nbd server if a client sent unexpected data during connection negotiation. A remote user or process could use this flaw to crash the qemu-nbd server resulting in denial of service.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=2b0bbc4f8809c972bad134bc1a2570dbb01dea0b
- https://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=ff82911cd3f69f028f2537825c9720ff78bc3f19
- http://www.securityfocus.com/bid/99944
- https://access.redhat.com/errata/RHSA-2017:2628
- https://access.redhat.com/errata/RHSA-2017:3466
- https://access.redhat.com/errata/RHSA-2017:3470
- https://access.redhat.com/errata/RHSA-2017:3471
- https://access.redhat.com/errata/RHSA-2017:3472
- https://access.redhat.com/errata/RHSA-2017:3473
- https://access.redhat.com/errata/RHSA-2017:3474
- http://www.openwall.com/lists/oss-security/2017/07/21/4
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7539
