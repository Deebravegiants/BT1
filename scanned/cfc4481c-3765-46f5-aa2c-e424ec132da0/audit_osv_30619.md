# [H] ALSA: 6fire: Release resources at card release

## Summary
Severity: High
Advisory: CVE-2024-53239
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53239
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: 6fire: Release resources at card release

The current 6fire code tries to release the resources right after the
call of usb6fire_chip_abort().  But at this moment, the card object
might be still in use (as we're calling snd_card_free_when_closed()).

For avoid potential UAFs, move the release of resources to the card's
private_free instead of the manual call of usb6fire_chip_destroy() at
the USB disconnect callback.

## References
- https://git.kernel.org/stable/c/0df7f4b5cc10f5adf98be0845372e9eef7bb5b09
- https://git.kernel.org/stable/c/273eec23467dfbfbd0e4c10302579ba441fb1e13
- https://git.kernel.org/stable/c/57860a80f03f9dc69a34a5c37b0941ad032a0a8c
- https://git.kernel.org/stable/c/74357d0b5cd3ef544752bc9f21cbeee4902fae6c
- https://git.kernel.org/stable/c/a0810c3d6dd2d29a9b92604d682eacd2902ce947
- https://git.kernel.org/stable/c/b754e831a94f82f2593af806741392903f359168
- https://git.kernel.org/stable/c/b889a7d68d7e76b8795b754a75c91a2d561d5e8c
- https://git.kernel.org/stable/c/ea8cc56db659cf0ae57073e32a4735ead7bd7ee3
- https://git.kernel.org/stable/c/f2d06d4e129e2508e356136f99bb20a332ff1a00
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53239.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53239
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
