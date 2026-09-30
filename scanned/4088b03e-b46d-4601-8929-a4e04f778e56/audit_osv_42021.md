# [H] HID: multitouch: fix out-of-bounds bit access on mt_io_flags

## Summary
Severity: High
Advisory: CVE-2026-64364
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64364
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.39, >=6.18.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: multitouch: fix out-of-bounds bit access on mt_io_flags

mt_io_flags is a single unsigned long, but mt_process_slot(),
mt_release_pending_palms() and mt_release_contacts() use it as a
per-slot bitmap indexed by the slot number. That slot number is only
bounded by td->maxcontacts, which is taken from the device's
ContactCountMaximum feature report and can be up to 255, not by
BITS_PER_LONG.

As a result, a multitouch device that advertises a large contact count
makes set_bit()/clear_bit() operate past the mt_io_flags word and
corrupt the adjacent members of struct mt_device. The sticky-fingers
release timer is the easiest way to reach this. mt_release_contacts()
runs

	for (i = 0; i < mt->num_slots; i++)
		clear_bit(i, &td->mt_io_flags);

with num_slots == maxcontacts. For maxcontacts around 250 the loop
clears the bits that overlap td->applications.next, zeroing that list
head, and the list_for_each_entry() that immediately follows then
dereferences NULL. The kernel panics from timer (softirq) context. On a
KASAN build this shows up as a general protection fault in
mt_release_contacts() with a null-ptr-deref at offset 0x58, which is
offsetof(struct mt_application, num_received).

The state is reachable from an untrusted USB or Bluetooth HID
multitouch device; no local privileges are required.

Store the per-slot active state in a separately allocated bitmap sized
for maxcontacts, the same pattern already used for pending_palm_slots,
and keep only MT_IO_FLAGS_RUNNING in mt_io_flags. The two
"mt_io_flags & MT_IO_SLOTS_MASK" arming checks become
bitmap_empty(td->active_slots, td->maxcontacts).

Move MT_IO_FLAGS_RUNNING back to bit 0. It was bumped to bit 32 by the
same commit to leave the low byte for the slot bits; with the slot bits
gone it fits in bit 0 again, which also keeps it within the unsigned
long on 32-bit.

## References
- https://git.kernel.org/stable/c/12e90656e330ff8bbaf2f29c535fdb8a11cc6f55
- https://git.kernel.org/stable/c/152983d87387f6a8ae72b73474cfa55fbcf1ec75
- https://git.kernel.org/stable/c/37daa8c96bd563d03150e23f094cb60703594a6d
- https://git.kernel.org/stable/c/6493ebf9489efef0105078377b973ab33d51af22
- https://git.kernel.org/stable/c/8813b0612275cc61fe9e6603d0ee019247ade6be
- https://git.kernel.org/stable/c/a6d5ce2e1a2d7bf189bde8a659d04b65f0b0725d
- https://git.kernel.org/stable/c/b5c037d6b807017e74a115288f81bc9cd5a5aab8
- https://git.kernel.org/stable/c/e24918ee67c4dc3d20d4670750e46e9b160365f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64364.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64364
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
