# [H] media: uvcvideo: Return queued buffers on start_streaming() failure

## Summary
Severity: High
Advisory: CVE-2026-43290
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43290
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: uvcvideo: Return queued buffers on start_streaming() failure

Return buffers if streaming fails to start due to uvc_pm_get() error.

This bug may be responsible for a warning I got running

    while :; do yavta -c3 /dev/video0; done

on an xHCI controller which failed under this workload.
I had no luck reproducing this warning again to confirm.

xhci_hcd 0000:09:00.0: HC died; cleaning up
usb 13-2: USB disconnect, device number 2
WARNING: CPU: 2 PID: 29386 at drivers/media/common/videobuf2/videobuf2-core.c:1803 vb2_start_streaming+0xac/0x120

## References
- https://git.kernel.org/stable/c/4cf3b6fd54ebb1ebc977bdc47fb6cfcf9a471a22
- https://git.kernel.org/stable/c/69c32df23bed6001864779b965fa009bcd9a26de
- https://git.kernel.org/stable/c/a5c01f15809d1d2c319d8bfb11d071df11ab731c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43290.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43290
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
