# [H] CVE-2018-5344

## Summary
Severity: High
Advisory: CVE-2018-5344
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-12
Source: https://osv.dev/vulnerability/CVE-2018-5344
Type: osv

## Details
In the Linux kernel through 4.14.13, drivers/block/loop.c mishandles lo_release serialization, which allows attackers to cause a denial of service (__lock_acquire use-after-free) or possibly have unspecified other impact.

## References
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3083
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3617-1/
- https://access.redhat.com/errata/RHSA-2018:3096
- https://usn.ubuntu.com/3583-2/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3632-1/
- http://www.securityfocus.com/bid/102503
- https://github.com/torvalds/linux/commit/ae6650163c66a7eff1acd6eb8b0f752dcfa8eba5
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ae6650163c66a7eff1acd6eb8b0f752dcfa8eba5
