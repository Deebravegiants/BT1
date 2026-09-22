# [H] HID: hid-thrustmaster: fix stack-out-of-bounds read in usb_check_int_endpoints()

## Summary
Severity: High
Advisory: CVE-2025-21794
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21794
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.76 <6.6.79, >=6.12.13 <6.12.16, >=6.13.2 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: hid-thrustmaster: fix stack-out-of-bounds read in usb_check_int_endpoints()

Syzbot[1] has detected a stack-out-of-bounds read of the ep_addr array from
hid-thrustmaster driver. This array is passed to usb_check_int_endpoints
function from usb.c core driver, which executes a for loop that iterates
over the elements of the passed array. Not finding a null element at the end of
the array, it tries to read the next, non-existent element, crashing the kernel.

To fix this, a 0 element was added at the end of the array to break the for
loop.

[1] https://syzkaller.appspot.com/bug?extid=9c9179ac46169c56c1ad

## References
- https://git.kernel.org/stable/c/0b43d98ff29be3144e86294486b1373b5df74c0e
- https://git.kernel.org/stable/c/436f48c864186e9413d1b7c6e91767cc9e1a65b8
- https://git.kernel.org/stable/c/73e36a699b9f46322ffb81f072a24e64f728dba7
- https://git.kernel.org/stable/c/cdd9a1ea23ff1a272547217100663e8de4eada40
- https://git.kernel.org/stable/c/f3ce05283f6cb6e19c220f5382def43dc5bd56b9
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21794.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21794
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
