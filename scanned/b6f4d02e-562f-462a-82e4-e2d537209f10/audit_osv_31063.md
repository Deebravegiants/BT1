# [H] ALSA: seq: oss: Fix races at processing SysEx messages

## Summary
Severity: High
Advisory: CVE-2024-57893
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57893
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.1.124, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: seq: oss: Fix races at processing SysEx messages

OSS sequencer handles the SysEx messages split in 6 bytes packets, and
ALSA sequencer OSS layer tries to combine those.  It stores the data
in the internal buffer and this access is racy as of now, which may
lead to the out-of-bounds access.

As a temporary band-aid fix, introduce a mutex for serializing the
process of the SysEx message packets.

## References
- https://git.kernel.org/stable/c/0179488ca992d79908b8e26b9213f1554fc5bacc
- https://git.kernel.org/stable/c/9d382112b36382aa65aad765f189ebde9926c101
- https://git.kernel.org/stable/c/cff1de87ed14fc0f2332213d2367100e7ad0753a
- https://git.kernel.org/stable/c/d2392b79d8af3714ea8878b71c66dc49d3110f44
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57893.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57893
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
