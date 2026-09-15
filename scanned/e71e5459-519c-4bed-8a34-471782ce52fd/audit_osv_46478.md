# [M] CVE-2011-5321

## Summary
Severity: Medium
Advisory: CVE-2011-5321
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2011-5321
Type: osv

## Details
The tty_open function in drivers/tty/tty_io.c in the Linux kernel before 3.1.1 mishandles a driver-lookup failure, which allows local users to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact via crafted access to a device file under the /dev/pts directory.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c290f8358acaeffd8e0c551ddcc24d1206143376
- http://rhn.redhat.com/errata/RHSA-2015-1221.html
- https://github.com/torvalds/linux/commit/c290f8358acaeffd8e0c551ddcc24d1206143376
- https://bugzilla.redhat.com/show_bug.cgi?id=1201887
- http://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.1.1
- http://www.openwall.com/lists/oss-security/2015/03/13/17
