# [H] CVE-2017-5546

## Summary
Severity: High
Advisory: CVE-2017-5546
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-5546
Type: osv

## Details
The freelist-randomization feature in mm/slab.c in the Linux kernel 4.8.x and 4.9.x before 4.9.5 allows local users to cause a denial of service (duplicate freelist entries and system crash) or possibly have unspecified other impact in opportunistic circumstances by leveraging the selection of a large value for a random number.

## References
- http://www.securityfocus.com/bid/95711
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.5
- https://bugzilla.redhat.com/show_bug.cgi?id=1415733
- https://github.com/torvalds/linux/commit/c4e490cf148e85ead0d1b1c2caaba833f1d5b29f
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c4e490cf148e85ead0d1b1c2caaba833f1d5b29f
- http://www.openwall.com/lists/oss-security/2017/01/21/3
