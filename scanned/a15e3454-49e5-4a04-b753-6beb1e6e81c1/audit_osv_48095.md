# [H] CVE-2017-18079

## Summary
Severity: High
Advisory: CVE-2017-18079
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-29
Source: https://osv.dev/vulnerability/CVE-2017-18079
Type: osv

## Details
drivers/input/serio/i8042.c in the Linux kernel before 4.12.4 allows attackers to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact because the port->exists value can change after it is validated.

## References
- http://www.securityfocus.com/bid/102895
- https://usn.ubuntu.com/3655-1/
- https://usn.ubuntu.com/3655-2/
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.4
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=340d394a789518018f834ff70f7534fc463d3226
- https://github.com/torvalds/linux/commit/340d394a789518018f834ff70f7534fc463d3226
