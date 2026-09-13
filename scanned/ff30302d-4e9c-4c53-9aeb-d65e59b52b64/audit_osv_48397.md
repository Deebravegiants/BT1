# [M] CVE-2017-7273

## Summary
Severity: Medium
Advisory: CVE-2017-7273
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2017-7273
Type: osv

## Details
The cp_report_fixup function in drivers/hid/hid-cypress.c in the Linux kernel 3.2 and 4.x before 4.9.4 allows physically proximate attackers to cause a denial of service (integer underflow) or possibly have unspecified other impact via a crafted HID report.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4faec4a2ef5dd481682cc155cb9ea14ba2534b76
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.4
- http://www.securityfocus.com/bid/97190
- https://github.com/torvalds/linux/commit/1ebb71143758f45dc0fa76e2f48429e13b16d110
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1ebb71143758f45dc0fa76e2f48429e13b16d110
