# [M] CVE-2017-8925

## Summary
Severity: Medium
Advisory: CVE-2017-8925
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/CVE-2017-8925
Type: osv

## Details
The omninet_open function in drivers/usb/serial/omninet.c in the Linux kernel before 4.10.4 allows local users to cause a denial of service (tty exhaustion) by leveraging reference count mishandling.

## References
- http://www.debian.org/security/2017/dsa-3886
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.4
- http://www.securityfocus.com/bid/98462
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=30572418b445d85fcfe6c8fe84c947d2606767d8
- https://github.com/torvalds/linux/commit/30572418b445d85fcfe6c8fe84c947d2606767d8
