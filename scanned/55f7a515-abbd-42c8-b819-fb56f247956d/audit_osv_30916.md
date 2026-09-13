# [M] mfd: intel_soc_pmic_bxtwc: Use IRQ domain for TMU device

## Summary
Severity: Medium
Advisory: CVE-2024-56724
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56724
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mfd: intel_soc_pmic_bxtwc: Use IRQ domain for TMU device

While design wise the idea of converting the driver to use
the hierarchy of the IRQ chips is correct, the implementation
has (inherited) flaws. This was unveiled when platform_get_irq()
had started WARN() on IRQ 0 that is supposed to be a Linux
IRQ number (also known as vIRQ).

Rework the driver to respect IRQ domain when creating each MFD
device separately, as the domain is not the same for all of them.

## References
- https://git.kernel.org/stable/c/1b734ad0e33648c3988c6a37c2ac16c2d63eda06
- https://git.kernel.org/stable/c/2310f5336f32eac9ada2d59b965d578efe25c4bf
- https://git.kernel.org/stable/c/56acf415772ee7e10e448b371f52b249aa2d0f7b
- https://git.kernel.org/stable/c/5bc6d0da4a32fe34a9960de577e0b7de3454de0c
- https://git.kernel.org/stable/c/9b79d59e6b2b515eb9a22bc469ef7b8f0904fc73
- https://git.kernel.org/stable/c/b7c7c400de85d915e0da7c2c363553a801c47349
- https://git.kernel.org/stable/c/c472b55cc0bc3df805db6a14f50a084884cf18ee
- https://git.kernel.org/stable/c/da498e02c92e6d82df8001438dd583b90c570815
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56724.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56724
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
