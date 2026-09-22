# [H] USB: Gadget: core: Help prevent panic during UVC unconfigure

## Summary
Severity: High
Advisory: CVE-2023-53580
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53580
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.46, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: Gadget: core: Help prevent panic during UVC unconfigure

Avichal Rakesh reported a kernel panic that occurred when the UVC
gadget driver was removed from a gadget's configuration.  The panic
involves a somewhat complicated interaction between the kernel driver
and a userspace component (as described in the Link tag below), but
the analysis did make one thing clear: The Gadget core should
accomodate gadget drivers calling usb_gadget_deactivate() as part of
their unbind procedure.

Currently this doesn't work.  gadget_unbind_driver() calls
driver->unbind() while holding the udc->connect_lock mutex, and
usb_gadget_deactivate() attempts to acquire that mutex, which will
result in a deadlock.

The simple fix is for gadget_unbind_driver() to release the mutex when
invoking the ->unbind() callback.  There is no particular reason for
it to be holding the mutex at that time, and the mutex isn't held
while the ->bind() callback is invoked.  So we'll drop the mutex
before performing the unbind callback and reacquire it afterward.

We'll also add a couple of comments to usb_gadget_activate() and
usb_gadget_deactivate().  Because they run in process context they
must not be called from a gadget driver's ->disconnect() callback,
which (according to the kerneldoc for struct usb_gadget_driver in
include/linux/usb/gadget.h) may run in interrupt context.  This may
help prevent similar bugs from arising in the future.

## References
- https://git.kernel.org/stable/c/65dadb2beeb7360232b09ebc4585b54475dfee06
- https://git.kernel.org/stable/c/8c1edc00db65f6d4408b3d1cd845e8da3b9e0ca4
- https://git.kernel.org/stable/c/bed19d95fcb9c98dfaa9585922b39a2dfba7898d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53580.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53580
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
