# [H] CVE-2015-8830

## Summary
Severity: High
Advisory: CVE-2015-8830
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2015-8830
Type: osv

## Details
Integer overflow in the aio_setup_single_vector function in fs/aio.c in the Linux kernel 4.0 allows local users to cause a denial of service or possibly have unspecified other impact via a large AIO iovec.  NOTE: this vulnerability exists because of a CVE-2012-6701 regression.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4c185ce06dca14f5cea192f5a2c981ef50663f2b
- http://www.debian.org/security/2016/dsa-3503
- http://www.ubuntu.com/usn/USN-2968-1
- http://www.ubuntu.com/usn/USN-2968-2
- http://www.ubuntu.com/usn/USN-2969-1
- http://www.ubuntu.com/usn/USN-2970-1
- https://access.redhat.com/errata/RHSA-2018:1854
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- https://github.com/torvalds/linux/commit/4c185ce06dca14f5cea192f5a2c981ef50663f2b
- https://github.com/torvalds/linux/commit/c4f4b82694fe48b02f7a881a1797131a6dad1364
- https://bugzilla.redhat.com/show_bug.cgi?id=1314275
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c4f4b82694fe48b02f7a881a1797131a6dad1364
- http://www.openwall.com/lists/oss-security/2016/03/02/9
