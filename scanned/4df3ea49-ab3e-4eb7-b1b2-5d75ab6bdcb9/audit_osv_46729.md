# [H] CVE-2014-9904

## Summary
Severity: High
Advisory: CVE-2014-9904
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2014-9904
Type: osv

## Details
The snd_compress_check_input function in sound/core/compress_offload.c in the ALSA subsystem in the Linux kernel before 3.17 does not properly check for an integer overflow, which allows local users to cause a denial of service (insufficient memory allocation) or possibly have unspecified other impact via a crafted SNDRV_COMPRESS_SET_PARAMS ioctl call.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6217e5ede23285ddfee10d2e4ba0cc2d4c046205
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- http://www.debian.org/security/2016/dsa-3616
- http://www.securityfocus.com/bid/91510
- http://www.securitytracker.com/id/1036189
- https://github.com/torvalds/linux/commit/6217e5ede23285ddfee10d2e4ba0cc2d4c046205
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6217e5ede23285ddfee10d2e4ba0cc2d4c046205
- https://github.com/torvalds/linux/commit/6217e5ede23285ddfee10d2e4ba0cc2d4c046205
