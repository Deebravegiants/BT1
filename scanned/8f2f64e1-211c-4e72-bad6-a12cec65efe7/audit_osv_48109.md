# [M] CVE-2017-18221

## Summary
Severity: Medium
Advisory: CVE-2017-18221
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-07
Source: https://osv.dev/vulnerability/CVE-2017-18221
Type: osv

## Details
The __munlock_pagevec function in mm/mlock.c in the Linux kernel before 4.11.4 allows local users to cause a denial of service (NR_MLOCK accounting corruption) via crafted use of mlockall and munlockall system calls.

## References
- https://usn.ubuntu.com/3655-2/
- https://usn.ubuntu.com/3655-1/
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.4
- http://www.securityfocus.com/bid/103321
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=70feee0e1ef331b22cc51f383d532a0d043fbdcc
- https://github.com/torvalds/linux/commit/70feee0e1ef331b22cc51f383d532a0d043fbdcc
