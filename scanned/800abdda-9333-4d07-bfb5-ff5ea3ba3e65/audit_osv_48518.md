# [M] CVE-2017-8924

## Summary
Severity: Medium
Advisory: CVE-2017-8924
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/CVE-2017-8924
Type: osv

## Details
The edge_bulk_in_callback function in drivers/usb/serial/io_ti.c in the Linux kernel before 4.10.4 allows local users to obtain sensitive information (in the dmesg ringbuffer and syslog) from uninitialized kernel memory by using a crafted USB device (posing as an io_ti USB serial device) to trigger an integer underflow.

## References
- http://www.debian.org/security/2017/dsa-3886
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.4
- http://www.securityfocus.com/bid/98451
- https://github.com/torvalds/linux/commit/654b404f2a222f918af9b0cd18ad469d0c941a8e
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=654b404f2a222f918af9b0cd18ad469d0c941a8e
