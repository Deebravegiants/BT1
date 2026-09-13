# [H] ALSA: usb-audio: Cancel pending work at closing a MIDI substream

## Summary
Severity: High
Advisory: CVE-2022-49545
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49545
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usb-audio: Cancel pending work at closing a MIDI substream

At closing a USB MIDI output substream, there might be still a pending
work, which would eventually access the rawmidi runtime object that is
being released.  For fixing the race, make sure to cancel the pending
work at closing.

## References
- https://git.kernel.org/stable/c/0125de38122f0f66bf61336158d12a1aabfe6425
- https://git.kernel.org/stable/c/11868ca21585561659c2575b0d6508ef8e9c4291
- https://git.kernel.org/stable/c/40bdb5ec957aca5c5c1924602bef6b0ab18e22d3
- https://git.kernel.org/stable/c/517dcef4d2dda0132648f1e4c079ed17bba4d1a4
- https://git.kernel.org/stable/c/5e5fe2b6065541c6216a7a003b0cddf386be0d2d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49545.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49545
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
