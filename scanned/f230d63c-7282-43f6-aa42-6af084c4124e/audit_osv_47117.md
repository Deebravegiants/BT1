# [H] CVE-2015-8961

## Summary
Severity: High
Advisory: CVE-2015-8961
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2015-8961
Type: osv

## Details
The __ext4_journal_stop function in fs/ext4/ext4_jbd2.c in the Linux kernel before 4.3.3 allows local users to gain privileges or cause a denial of service (use-after-free) by leveraging improper access to a certain error field.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6934da9238da947628be83635e365df41064b09b
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.3
- http://www.securityfocus.com/bid/94135
- https://github.com/torvalds/linux/commit/6934da9238da947628be83635e365df41064b09b
- https://source.android.com/security/bulletin/2016-11-01.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6934da9238da947628be83635e365df41064b09b
- https://github.com/torvalds/linux/commit/6934da9238da947628be83635e365df41064b09b
