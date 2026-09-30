# [M] CVE-2017-7616

## Summary
Severity: Medium
Advisory: CVE-2017-7616
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-04-10
Source: https://osv.dev/vulnerability/CVE-2017-7616
Type: osv

## Details
Incorrect error handling in the set_mempolicy and mbind compat syscalls in mm/mempolicy.c in the Linux kernel through 4.10.9 allows local users to obtain sensitive information from uninitialized stack data by triggering failure of a certain bitmap operation.

## References
- https://source.android.com/security/bulletin/2017-09-01
- http://www.securitytracker.com/id/1038503
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2018:1854
- http://www.securityfocus.com/bid/97527
- https://github.com/torvalds/linux/commit/cf01fb9985e8deb25ccf0ea54d916b8871ae0e62
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cf01fb9985e8deb25ccf0ea54d916b8871ae0e62
