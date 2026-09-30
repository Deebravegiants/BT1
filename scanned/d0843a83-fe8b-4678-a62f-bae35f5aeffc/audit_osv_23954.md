# [M] nfc: nfcmrvl: Fix memory leak in nfcmrvl_play_deferred

## Summary
Severity: Medium
Advisory: CVE-2022-49729
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49729
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <4.9.320, >=4.10.0 <4.14.285, >=4.15.0 <4.19.249, >=4.20.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: nfcmrvl: Fix memory leak in nfcmrvl_play_deferred

Similar to the handling of play_deferred in commit 19cfe912c37b
("Bluetooth: btusb: Fix memory leak in play_deferred"), we thought
a patch might be needed here as well.

Currently usb_submit_urb is called directly to submit deferred tx
urbs after unanchor them.

So the usb_giveback_urb_bh would failed to unref it in usb_unanchor_urb
and cause memory leak.

Put those urbs in tx_anchor to avoid the leak, and also fix the error
handling.

## References
- https://git.kernel.org/stable/c/0eeec1a8b0cd38c47edeb042980a6aeacecf35ed
- https://git.kernel.org/stable/c/1eb0afecfb9cd0f38424b82bd9aaa542310934ee
- https://git.kernel.org/stable/c/3e7c7df6991ac349f2fa8540047757df666e610f
- https://git.kernel.org/stable/c/3eadc560c1919b8193d17334145dad9a917960e4
- https://git.kernel.org/stable/c/6616872cfe7f0474a22dd1f12699f95bcf81a54d
- https://git.kernel.org/stable/c/6b4d8b44e7163a77fe942f5b80e1651c1b78c537
- https://git.kernel.org/stable/c/8a4d480702b71184fabcf379b80bf7539716752e
- https://git.kernel.org/stable/c/f21f908347712b8288ffe83b531b5e977042b29c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49729.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49729
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
