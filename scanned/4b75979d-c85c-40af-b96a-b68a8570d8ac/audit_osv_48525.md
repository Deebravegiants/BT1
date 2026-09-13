# [M] CVE-2017-9059

## Summary
Severity: Medium
Advisory: CVE-2017-9059
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9059
Type: osv

## Details
The NFSv4 implementation in the Linux kernel through 4.11.1 allows local users to cause a denial of service (resource consumption) by leveraging improper channel callback shutdown when unmounting an NFSv4 filesystem, aka a "module reference and kernel daemon" leak.

## References
- http://www.securityfocus.com/bid/98551
- https://bugzilla.redhat.com/show_bug.cgi?id=1451386
- https://github.com/torvalds/linux/commit/c70422f760c120480fee4de6c38804c72aa26bc1
- https://www.spinics.net/lists/linux-nfs/msg63334.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c70422f760c120480fee4de6c38804c72aa26bc1
