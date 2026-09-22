# [H] CVE-2012-6703

## Summary
Severity: High
Advisory: CVE-2012-6703
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-29
Source: https://osv.dev/vulnerability/CVE-2012-6703
Type: osv

## Details
Integer overflow in the snd_compr_allocate_buffer function in sound/core/compress_offload.c in the ALSA subsystem in the Linux kernel before 3.6-rc6-next-20120917 allows local users to cause a denial of service (insufficient memory allocation) or possibly have unspecified other impact via a crafted SNDRV_COMPRESS_SET_PARAMS ioctl call.

## References
- https://github.com/torvalds/linux/commit/b35cc8225845112a616e3a2266d2fde5ab13d3ab
- https://bugzilla.redhat.com/show_bug.cgi?id=1351076
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b35cc8225845112a616e3a2266d2fde5ab13d3ab
- http://www.openwall.com/lists/oss-security/2016/06/28/6
- http://www.securityfocus.com/bid/91502
- http://www.securitytracker.com/id/1036190
- https://www.kernel.org/pub/linux/kernel/next/patch-v3.6-rc6-next-20120917.xz
