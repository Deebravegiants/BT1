# [M] CVE-2017-16528

## Summary
Severity: Medium
Advisory: CVE-2017-16528
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16528
Type: osv

## Details
sound/core/seq_device.c in the Linux kernel before 4.13.4 allows local users to cause a denial of service (snd_rawmidi_dev_seq_free use-after-free and system crash) or possibly have unspecified other impact via a crafted USB device.

## References
- https://groups.google.com/d/msg/syzkaller/kuZzDHGkQu8/5du20rZEAAAJ
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://github.com/torvalds/linux/commit/fc27fe7e8deef2f37cba3f2be2d52b6ca5eb9d57
