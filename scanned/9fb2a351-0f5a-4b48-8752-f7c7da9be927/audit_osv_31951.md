# [M] media: streamzap: fix race between device disconnection and urb callback

## Summary
Severity: Medium
Advisory: CVE-2025-22027
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22027
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: streamzap: fix race between device disconnection and urb callback

Syzkaller has reported a general protection fault at function
ir_raw_event_store_with_filter(). This crash is caused by a NULL pointer
dereference of dev->raw pointer, even though it is checked for NULL in
the same function, which means there is a race condition. It occurs due
to the incorrect order of actions in the streamzap_disconnect() function:
rc_unregister_device() is called before usb_kill_urb(). The dev->raw
pointer is freed and set to NULL in rc_unregister_device(), and only
after that usb_kill_urb() waits for in-progress requests to finish.

If rc_unregister_device() is called while streamzap_callback() handler is
not finished, this can lead to accessing freed resources. Thus
rc_unregister_device() should be called after usb_kill_urb().

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

## References
- https://git.kernel.org/stable/c/15483afb930fc2f883702dc96f80efbe4055235e
- https://git.kernel.org/stable/c/30ef7cfee752ca318d5902cb67b60d9797ccd378
- https://git.kernel.org/stable/c/4db62b60af2ccdea6ac5452fd20e29587ed85f57
- https://git.kernel.org/stable/c/8760da4b9d44c36b93b6e4cf401ec7fe520015bd
- https://git.kernel.org/stable/c/adf0ddb914c9e5b3e50da4c97959e82de2df75c3
- https://git.kernel.org/stable/c/e11652a6514ec805440c1bb3739e6c6236fffcc7
- https://git.kernel.org/stable/c/f1d518c0bad01abe83c2df880274cb6a39f4a457
- https://git.kernel.org/stable/c/f656cfbc7a293a039d6a0c7100e1c846845148c1
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22027.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22027
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
