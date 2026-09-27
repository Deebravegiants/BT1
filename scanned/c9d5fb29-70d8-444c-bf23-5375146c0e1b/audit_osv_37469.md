# [H] Input: uinput - fix circular locking dependency with ff-core

## Summary
Severity: High
Advisory: CVE-2026-31667
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31667
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: uinput - fix circular locking dependency with ff-core

A lockdep circular locking dependency warning can be triggered
reproducibly when using a force-feedback gamepad with uinput (for
example, playing ELDEN RING under Wine with a Flydigi Vader 5
controller):

  ff->mutex -> udev->mutex -> input_mutex -> dev->mutex -> ff->mutex

The cycle is caused by four lock acquisition paths:

1. ff upload: input_ff_upload() holds ff->mutex and calls
   uinput_dev_upload_effect() -> uinput_request_submit() ->
   uinput_request_send(), which acquires udev->mutex.

2. device create: uinput_ioctl_handler() holds udev->mutex and calls
   uinput_create_device() -> input_register_device(), which acquires
   input_mutex.

3. device register: input_register_device() holds input_mutex and
   calls kbd_connect() -> input_register_handle(), which acquires
   dev->mutex.

4. evdev release: evdev_release() calls input_flush_device() under
   dev->mutex, which calls input_ff_flush() acquiring ff->mutex.

Fix this by introducing a new state_lock spinlock to protect
udev->state and udev->dev access in uinput_request_send() instead of
acquiring udev->mutex.  The function only needs to atomically check
device state and queue an input event into the ring buffer via
uinput_dev_event() -- both operations are safe under a spinlock
(ktime_get_ts64() and wake_up_interruptible() do not sleep).  This
breaks the ff->mutex -> udev->mutex link since a spinlock is a leaf in
the lock ordering and cannot form cycles with mutexes.

To keep state transitions visible to uinput_request_send(), protect
writes to udev->state in uinput_create_device() and
uinput_destroy_device() with the same state_lock spinlock.

Additionally, move init_completion(&request->done) from
uinput_request_send() to uinput_request_submit() before
uinput_request_reserve_slot().  Once the slot is allocated,
uinput_flush_requests() may call complete() on it at any time from
the destroy path, so the completion must be initialised before the
request becomes visible.

Lock ordering after the fix:

  ff->mutex -> state_lock (spinlock, leaf)
  udev->mutex -> state_lock (spinlock, leaf)
  udev->mutex -> input_mutex -> dev->mutex -> ff->mutex (no back-edge)

## References
- https://git.kernel.org/stable/c/1534661043c434b81cfde26b97a2fb2460329cf0
- https://git.kernel.org/stable/c/1e09dfbb4f5d20ee111f92325a00f85778a5f328
- https://git.kernel.org/stable/c/271ee71a1917b89f6d73ec82dd091c33d92ee617
- https://git.kernel.org/stable/c/4cda78d6f8bf2b700529f2fbccb994c3e826d7c2
- https://git.kernel.org/stable/c/546c18a14924eb521fe168d916d7ce28f1e13c1d
- https://git.kernel.org/stable/c/71a9729f412e2c692a35c542e14b706fb342927f
- https://git.kernel.org/stable/c/974f7b138c3a96dd5cd53d1b33409cd7b2229dc6
- https://git.kernel.org/stable/c/a3d6c9c053c9c605651508569230ead633b13f76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31667.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31667
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
