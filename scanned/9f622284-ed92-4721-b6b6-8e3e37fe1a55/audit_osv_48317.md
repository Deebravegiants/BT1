# [H] CVE-2017-6345

## Summary
Severity: High
Advisory: CVE-2017-6345
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-6345
Type: osv

## Details
The LLC subsystem in the Linux kernel before 4.9.13 does not ensure that a certain destructor exists in required circumstances, which allows local users to cause a denial of service (BUG_ON) or possibly have unspecified other impact via crafted system calls.

## References
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/96510
- http://www.debian.org/security/2017/dsa-3804
- https://github.com/torvalds/linux/commit/8b74d439e1697110c5e5c600643e823eb1dd0762
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8b74d439e1697110c5e5c600643e823eb1dd0762
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.13
- http://www.openwall.com/lists/oss-security/2017/02/28/7
