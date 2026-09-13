# [H] ALSA: usb-audio: Clamp frame size in implicit-feedback mode

## Summary
Severity: High
Advisory: CVE-2026-74497
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74497
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usb-audio: Clamp frame size in implicit-feedback mode

snd_usb_handle_sync_urb() scales received sync packet sizes by the sender's
stride and stores the result directly in out_packet->packet_size[i]. If a
connected USB device sends an oversized sync packet, this frame count can
exceed ep->maxframesize.

The un-clamped frame count then propagates to the playback endpoint queue,
potentially driving packet transfers beyond the endpoint's hardware frame
limits.

Cap the calculated frame count against ep->maxframesize in
snd_usb_handle_sync_urb() to prevent oversized packets from entering the
playback queue.

## References
- https://git.kernel.org/stable/c/09cf3dbbb4256a43feb91d2f51f274510a9ada47
- https://git.kernel.org/stable/c/2d39fea6d3c19a2f5811d123114d92e3d0115fd1
- https://git.kernel.org/stable/c/2db4535d6af79276a64449201c5be5feffb31c64
- https://git.kernel.org/stable/c/53f0aa37eb945f3c983f61d12fc35eb33debb8a9
- https://git.kernel.org/stable/c/56ac3e7c90f6b45969c3fd07a98fad760ffd6901
- https://git.kernel.org/stable/c/8d7a30c50c2e58a6839634ed0acde14466d1dc61
- https://git.kernel.org/stable/c/be97fea7451d758881b95af78e900dd0d58a382a
- https://git.kernel.org/stable/c/cfa8d3e0e8b812c4db4d5241f62b6bdbab2bd7be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74497.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74497
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
