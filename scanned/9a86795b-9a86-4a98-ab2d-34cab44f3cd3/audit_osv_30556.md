# [H] ALSA: usb-audio: Fix out of bounds reads when finding clock sources

## Summary
Severity: High
Advisory: CVE-2024-53150
Aliases: A-382239029, ASB-A-382239029
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53150
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usb-audio: Fix out of bounds reads when finding clock sources

The current USB-audio driver code doesn't check bLength of each
descriptor at traversing for clock descriptors.  That is, when a
device provides a bogus descriptor with a shorter bLength, the driver
might hit out-of-bounds reads.

For addressing it, this patch adds sanity checks to the validator
functions for the clock descriptor traversal.  When the descriptor
length is shorter than expected, it's skipped in the loop.

For the clock source and clock multiplier descriptors, we can just
check bLength against the sizeof() of each descriptor type.
OTOH, the clock selector descriptor of UAC2 and UAC3 has an array
of bNrInPins elements and two more fields at its tail, hence those
have to be checked in addition to the sizeof() check.

## References
- https://git.kernel.org/stable/c/096bb5b43edf755bc4477e64004fa3a20539ec2f
- https://git.kernel.org/stable/c/45a92cbc88e4013bfed7fd2ccab3ade45f8e896b
- https://git.kernel.org/stable/c/74cb86e1006c5437b1d90084d22018da30fddc77
- https://git.kernel.org/stable/c/a3dd4d63eeb452cfb064a13862fb376ab108f6a6
- https://git.kernel.org/stable/c/a632bdcb359fd8145e86486ff8612da98e239acd
- https://git.kernel.org/stable/c/ab011f7439d9bbfd34fd3b9cef4b2d6d952c9bb9
- https://git.kernel.org/stable/c/da13ade87a12dd58829278bc816a61bea06a56a9
- https://git.kernel.org/stable/c/ea0fa76f61cf8e932d1d26e6193513230816e11d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-53150
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53150.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53150
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
