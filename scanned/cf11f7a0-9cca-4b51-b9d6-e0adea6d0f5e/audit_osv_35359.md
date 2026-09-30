# [H] gpio: mpsse: ensure worker is torn down

## Summary
Severity: High
Advisory: CVE-2025-71158
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-71158
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: mpsse: ensure worker is torn down

When an IRQ worker is running, unplugging the device would cause a
crash. The sealevel hardware this driver was written for was not
hotpluggable, so I never realized it.

This change uses a spinlock to protect a list of workers, which
it tears down on disconnect.

## References
- https://git.kernel.org/stable/c/179ef1127d7a4f09f0e741fa9f30b8a8e7886271
- https://git.kernel.org/stable/c/472d900c8bcac301ae0e40fdca7db799bd989ff5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71158.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71158
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
