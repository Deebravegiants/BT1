# [H] usb: gadget: f_midi: cancel pending IN work before freeing the midi object

## Summary
Severity: High
Advisory: CVE-2026-64584
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64584
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.265, >=5.11.0 <5.15.216, >=5.12.0 <6.1.183, >=5.16.0 <6.6.148, >=6.2.0 <6.12.101, >=6.7.0 <6.18.42, >=6.13.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: f_midi: cancel pending IN work before freeing the midi object

The f_midi driver embeds a work item (midi->work) whose handler,
f_midi_in_work(), dereferences the enclosing struct f_midi through
container_of().  This work is armed from two sites: f_midi_complete(),
on a normal IN-endpoint completion, and f_midi_in_trigger(), on an ALSA
rawmidi output-stream start.

Neither f_midi_disable() nor f_midi_unbind() cancels midi->work.
f_midi_disable() only disables the endpoints and drains the in_req_fifo;
it does not synchronize the work item, and the sound card is released
asynchronously to the final free of the midi object.

The midi object is reference-counted (midi->free_ref) and is freed in
f_midi_free() only once both the usb_function reference and the rawmidi
private_data reference have been dropped.  In f_midi_unbind(),
f_midi_disable() runs before the sound card is released, so while the
USB endpoints are already disabled the rawmidi device is still usable by
an open substream.  A concurrent userspace write on such a substream can
reach f_midi_in_trigger() and queue midi->work again after
f_midi_disable() has returned.  A work item armed this way may still be
pending when the last reference drops and f_midi_free() proceeds to
kfree(midi), letting f_midi_in_work() dereference the struct after it
has been freed, a use-after-free.

For this reason cancelling midi->work in f_midi_disable() would not be
sufficient: the ALSA trigger path can rearm the work after disable()
returns.  Cancelling at the refcount-zero free site is the boundary
after which neither arming source can survive, because by then both
references that keep the midi object alive have been dropped: the USB
endpoints are already disabled and the rawmidi device has been released.

Fix this by calling cancel_work_sync(&midi->work) in the refcount-zero
block of f_midi_free(), before the embedded work_struct is freed along
with the rest of the structure.  opts->lock is a sleeping mutex, so
calling cancel_work_sync() under it is permitted, and the handler takes
midi->transmit_lock rather than opts->lock, so no self-deadlock can
occur while it waits for a running instance of the work to finish.

This issue was found by an in-house static analysis tool.

## References
- https://git.kernel.org/stable/c/380b4bef46c2eb260c7a9c6bb2c5be33ce5a38f9
- https://git.kernel.org/stable/c/5650c18d93a1db7e27cb5a40b394747eb4686d5b
- https://git.kernel.org/stable/c/620955b222c47332297d6bf38f78541aa699238a
- https://git.kernel.org/stable/c/87bc316dd6fc90072297c635e10b9aa6075ecda1
- https://git.kernel.org/stable/c/ac9a51d910bb7465c554c45320cb6c09f3d0b49d
- https://git.kernel.org/stable/c/df18150126f66817e4d3f79f309e9c92d6ff384e
- https://git.kernel.org/stable/c/f3c6f2c38062703d3dc7f86958bb0790c6959add
- https://git.kernel.org/stable/c/f45089eaad0a083d71d84ff175741d7e157d9b69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64584.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64584
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
