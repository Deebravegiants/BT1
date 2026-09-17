# [M] CVE-2017-18208

## Summary
Severity: Medium
Advisory: CVE-2017-18208
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-18208
Type: osv

## Details
The madvise_willneed function in mm/madvise.c in the Linux kernel before 4.14.4 allows local users to cause a denial of service (infinite loop) by triggering use of MADVISE_WILLNEED for a DAX mapping.

## References
- https://usn.ubuntu.com/3653-1/
- https://usn.ubuntu.com/3655-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3653-2/
- https://usn.ubuntu.com/3655-2/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3657-1/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- https://access.redhat.com/errata/RHSA-2019:4058
- https://access.redhat.com/errata/RHSA-2019:3967
- https://github.com/torvalds/linux/commit/6ea8d958a2c95a1d514015d4e29ba21a8c0a1a91
- https://access.redhat.com/errata/RHSA-2019:4057
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.4
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6ea8d958a2c95a1d514015d4e29ba21a8c0a1a91
