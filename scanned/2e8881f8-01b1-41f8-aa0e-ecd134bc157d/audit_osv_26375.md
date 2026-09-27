# [M] firewire: fix memory leak for payload of request subaction to IEC 61883-1 FCP region

## Summary
Severity: Medium
Advisory: CVE-2023-52989
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52989
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <4.14.306, >=4.15.0 <4.19.273, >=4.20.0 <5.4.232, >=5.5.0 <5.10.168, >=5.11.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

firewire: fix memory leak for payload of request subaction to IEC 61883-1 FCP region

This patch is fix for Linux kernel v2.6.33 or later.

For request subaction to IEC 61883-1 FCP region, Linux FireWire subsystem
have had an issue of use-after-free. The subsystem allows multiple
user space listeners to the region, while data of the payload was likely
released before the listeners execute read(2) to access to it for copying
to user space.

The issue was fixed by a commit 281e20323ab7 ("firewire: core: fix
use-after-free regression in FCP handler"). The object of payload is
duplicated in kernel space for each listener. When the listener executes
ioctl(2) with FW_CDEV_IOC_SEND_RESPONSE request, the object is going to
be released.

However, it causes memory leak since the commit relies on call of
release_request() in drivers/firewire/core-cdev.c. Against the
expectation, the function is never called due to the design of
release_client_resource(). The function delegates release task
to caller when called with non-NULL fourth argument. The implementation
of ioctl_send_response() is the case. It should release the object
explicitly.

This commit fixes the bug.

## References
- https://git.kernel.org/stable/c/356ff89acdbe6a66019154bc7eb2d300f5b15103
- https://git.kernel.org/stable/c/531390a243ef47448f8bad01c186c2787666bf4d
- https://git.kernel.org/stable/c/53785fd9b315583cf029e39f72b73d23704a2253
- https://git.kernel.org/stable/c/5f4543c9382ae2d5062f6aa4fecae0c9258d0b0e
- https://git.kernel.org/stable/c/b2cd3947d116bb9ba7ff097b5fc747a8956764db
- https://git.kernel.org/stable/c/c8bdc88216f09cb7387fedbdf613524367328616
- https://git.kernel.org/stable/c/d5a2dcee53fa6e6e2822f93cb3f1b0cd23163bee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52989.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52989
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
