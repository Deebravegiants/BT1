# [H] ALSA: FCP: fix OOB write in fcp_meter_ctl_get()

## Summary
Severity: High
Advisory: CVE-2026-74640
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74640
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: FCP: fix OOB write in fcp_meter_ctl_get()

fcp_ioctl_set_meter_map() bounds the user-supplied Level Meter map size
by the driver's own limit of 255

	if (map.map_size < 1 || map.map_size > 255 ||
	    map.meter_slots < 1 || map.meter_slots > 255)
		return -EINVAL;

and passes it to fcp_add_new_ctl() as the control's channel count, where
it is stored as elem->channels.

Every control read writes into struct snd_ctl_elem_value, whose integer
array is declared long value[128], so the limit is 128, not 255.
fcp_meter_ctl_get() stores one 64-bit word per channel into that array
with no bound of its own:

	for (i = 0; i < elem->channels; i++) {
		int idx = private->meter_level_map[i];
		int value = idx < 0 ? 0 : le32_to_cpu(resp[idx]);

		ucontrol->value.integer.value[i] = value;
	}

snd_ctl_elem_read_user() serves that object from
memdup_user(_control, sizeof(*control)), 1224 bytes on LP64 out of
kmalloc-2048.  offsetof(struct snd_ctl_elem_value, value) is 72, so
element i is written at byte 72 + 8 * i and element 144 already lands
past the allocation.  At map_size 255 the last store ends at byte 2112,
888 bytes past the object and 64 bytes into the adjacent slab object.
The stored words come from the device and meter_level_map[] selects
which word lands in which slot, so extent and contents are both
controlled.

The core does not catch this.  snd_ctl_check_elem_info() is reached only
from __snd_ctl_elem_info(), which snd_ctl_elem_read() calls under
CONFIG_SND_CTL_DEBUG; without that option snd_ctl_skip_validation() is a
compile-time true.  __snd_ctl_add_replace() validates kcontrol->count and
never inspects elem->channels.

Installing an oversized map needs CAP_SYS_RAWIO, but the control outlives
the hwdep descriptor that created it, so the out-of-bounds stores are
issued by any process able to read controls on /dev/snd/controlC0.

KASAN on 7.2.0-rc5 (arm64), triggered by an unprivileged control read:

  BUG: KASAN: slab-out-of-bounds in fcp_meter_ctl_get
  Write of size 8 at addr ffff000017af04c8 by task fcp_trigger/185
   __asan_store8
   fcp_meter_ctl_get
   snd_ctl_elem_read
   snd_ctl_ioctl
  Allocated by task 185:
   memdup_user
   snd_ctl_ioctl
  The buggy address is located 0 bytes to the right of
   allocated 1224-byte region [ffff000017af0000, ffff000017af04c8)

Bound the map size by the ABI limit rather than by 255, and bound the
store loop at the sink so it cannot run past the value array whatever
elem->channels holds.

Discovered by XBOW, triaged by Baul Lee <baul.lee@xbow.com>

## References
- https://git.kernel.org/stable/c/620f1e52a46f604635efd0fb78138afd6a513b5d
- https://git.kernel.org/stable/c/bb30e35c36ed00f24fa39aded811f64230a913b0
- https://git.kernel.org/stable/c/bb61dc2ae59026f76db26e1909746908bc5b6f31
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74640.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74640
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
