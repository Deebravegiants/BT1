# [M] CVE-2019-14763

## Summary
Severity: Medium
Advisory: CVE-2019-14763
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-07
Source: https://osv.dev/vulnerability/CVE-2019-14763
Type: osv

## Details
In the Linux kernel before 4.16.4, a double-locking error in drivers/usb/dwc3/gadget.c may potentially cause a deadlock with f_hid.

## References
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.4
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4118-1/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=072684e8c58d17e853f8e8b9f6d9ce2e58d2b036
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c91815b596245fd7da349ecc43c8def670d2269e
- https://github.com/torvalds/linux/commit/c91815b596245fd7da349ecc43c8def670d2269e
- https://github.com/torvalds/linux/commit/072684e8c58d17e853f8e8b9f6d9ce2e58d2b036
- https://www.spinics.net/lists/linux-usb/msg167355.html
- https://www.spinics.net/lists/linux-usb/msg167393.html
