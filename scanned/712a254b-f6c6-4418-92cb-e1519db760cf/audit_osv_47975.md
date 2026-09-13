# [H] CVE-2017-15951

## Summary
Severity: High
Advisory: CVE-2017-15951
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-28
Source: https://osv.dev/vulnerability/CVE-2017-15951
Type: osv

## Details
The KEYS subsystem in the Linux kernel before 4.13.10 does not correctly synchronize the actions of updating versus finding a key in the "negative" state to avoid a race condition, which allows local users to cause a denial of service or possibly have unspecified other impact via crafted system calls.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.10
- http://www.securityfocus.com/bid/101621
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=363b02dab09b3226f3bd1420dad9c72b79a42a76
- https://github.com/torvalds/linux/commit/363b02dab09b3226f3bd1420dad9c72b79a42a76
