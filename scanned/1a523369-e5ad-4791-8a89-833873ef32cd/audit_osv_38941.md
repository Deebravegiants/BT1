# [H] ALSA: mixer: oss: Add card disconnect checkpoints

## Summary
Severity: High
Advisory: CVE-2026-43126
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43126
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: mixer: oss: Add card disconnect checkpoints

ALSA OSS mixer layer calls the kcontrol ops rather individually, and
pending calls might be not always caught at disconnecting the device.

For avoiding the potential UAF scenarios, add sanity checks of the
card disconnection at each entry point of OSS mixer accesses.  The
rwsem is taken just before that check, hence the rest context should
be covered by that properly.

## References
- https://git.kernel.org/stable/c/084d5d44418148662365eced3e126ad1a81ee3e2
- https://git.kernel.org/stable/c/8c097cf736993454acf3f711a3b376d6c7ad8965
- https://git.kernel.org/stable/c/ae583f113d15fa97e5234133c20d09f8e6214e47
- https://git.kernel.org/stable/c/e6645e625480cdf1079a4265f758d13b70721029
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43126.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43126
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
