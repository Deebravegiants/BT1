# [H] CVE-2017-2647

## Summary
Severity: High
Advisory: CVE-2017-2647
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-31
Source: https://osv.dev/vulnerability/CVE-2017-2647
Type: osv

## Details
The KEYS subsystem in the Linux kernel before 3.18 allows local users to gain privileges or cause a denial of service (NULL pointer dereference and system crash) via vectors involving a NULL value for a certain match field, related to the keyring_search_iterator function in keyring.c.

## References
- https://usn.ubuntu.com/3849-2/
- https://usn.ubuntu.com/3849-1/
- http://www.securityfocus.com/bid/97258
- https://access.redhat.com/errata/RHSA-2017:2437
- https://access.redhat.com/errata/RHSA-2017:2444
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c06cfb08b88dfbe13be44a69ae2fdc3a7c902d81
- https://bugzilla.redhat.com/show_bug.cgi?id=1428353
- https://github.com/torvalds/linux/commit/c06cfb08b88dfbe13be44a69ae2fdc3a7c902d81
