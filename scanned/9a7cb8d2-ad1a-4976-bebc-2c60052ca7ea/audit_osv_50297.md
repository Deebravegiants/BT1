# [H] CVE-2020-11725

## Summary
Severity: High
Advisory: CVE-2020-11725
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-12
Source: https://osv.dev/vulnerability/CVE-2020-11725
Type: osv

## Details
snd_ctl_elem_add in sound/core/control.c in the Linux kernel through 5.6.3 has a count=info->owner line, which later affects a private_size*count multiplication for unspecified "interesting side effects." NOTE: kernel engineers dispute this finding, because it could be relevant only if new callers were added that were unfamiliar with the misuse of the info->owner field to represent data unrelated to the "owner" concept. The existing callers, SNDRV_CTL_IOCTL_ELEM_ADD and SNDRV_CTL_IOCTL_ELEM_REPLACE, have been designed to misuse the info->owner field in a safe way

## References
- https://lore.kernel.org/alsa-devel/s5h4ktmlfpx.wl-tiwai%40suse.de/
- https://twitter.com/yabbadabbadrew/status/1248632267028582400
- https://github.com/torvalds/linux/blob/3b2549a3740efb8af0150415737067d87e466c5b/sound/core/control.c#L1434-L1474
