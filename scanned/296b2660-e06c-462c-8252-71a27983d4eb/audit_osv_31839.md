# [M] USB: gadget: f_midi: f_midi_complete to call queue_work

## Summary
Severity: Medium
Advisory: CVE-2025-21859
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21859
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.130, >=6.2.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: gadget: f_midi: f_midi_complete to call queue_work

When using USB MIDI, a lock is attempted to be acquired twice through a
re-entrant call to f_midi_transmit, causing a deadlock.

Fix it by using queue_work() to schedule the inner f_midi_transmit() via
a high priority work queue from the completion handler.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1f10923404705a94891e612dff3b75e828a78368
- https://git.kernel.org/stable/c/24a942610ee9bafb2692a456ae850c5b2e409b05
- https://git.kernel.org/stable/c/4ab37fcb42832cdd3e9d5e50653285ca84d6686f
- https://git.kernel.org/stable/c/727dee0857946b85232526de4f5a957fe163e89a
- https://git.kernel.org/stable/c/8aa6b4be1f4efccbfc533e6ec8841d26e4fa8dba
- https://git.kernel.org/stable/c/b09957657d7767d164b3432af2129bd72947553c
- https://git.kernel.org/stable/c/deeee3adb2c01eedab32c3b4519337689ad02e8a
- https://git.kernel.org/stable/c/e9fec6f42c45db2f62dc373fb1a10d2488c04e79
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21859.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21859
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
