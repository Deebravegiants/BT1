# [M] CVE-2016-6327

## Summary
Severity: Medium
Advisory: CVE-2016-6327
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2016-6327
Type: osv

## Details
drivers/infiniband/ulp/srpt/ib_srpt.c in the Linux kernel before 4.5.1 allows local users to cause a denial of service (NULL pointer dereference and system crash) by using an ABORT_TASK command to abort a device write operation.

## References
- http://www.securityfocus.com/bid/92549
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.1
- http://www.openwall.com/lists/oss-security/2016/08/19/5
- https://bugzilla.redhat.com/show_bug.cgi?id=1354525
- https://github.com/torvalds/linux/commit/51093254bf879bc9ce96590400a87897c7498463
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=51093254bf879bc9ce96590400a87897c7498463
