# [H] CVE-2015-8967

## Summary
Severity: High
Advisory: CVE-2015-8967
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/CVE-2015-8967
Type: osv

## Details
arch/arm64/kernel/sys.c in the Linux kernel before 4.0 allows local users to bypass the "strict page permissions" protection mechanism and modify the system-call table, and consequently gain privileges, by leveraging write access.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c623b33b4e9599c6ac5076f7db7369eb9869aa04
- http://source.android.com/security/bulletin/2016-12-01.html
- http://www.securityfocus.com/bid/94680
- https://github.com/torvalds/linux/commit/c623b33b4e9599c6ac5076f7db7369eb9869aa04
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c623b33b4e9599c6ac5076f7db7369eb9869aa04
- https://github.com/torvalds/linux/commit/c623b33b4e9599c6ac5076f7db7369eb9869aa04
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c623b33b4e9599c6ac5076f7db7369eb9869aa04
- https://github.com/torvalds/linux/commit/c623b33b4e9599c6ac5076f7db7369eb9869aa04
