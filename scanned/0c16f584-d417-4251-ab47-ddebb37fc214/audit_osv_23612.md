# [M] drm/tegra: Fix reference leak in tegra_dsi_ganged_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49216
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49216
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/tegra: Fix reference leak in tegra_dsi_ganged_probe

The reference taken by 'of_find_device_by_node()' must be released when
not needed anymore. Add put_device() call to fix this.

## References
- https://git.kernel.org/stable/c/0e2f4e434e71dffd1085c3dccd676514bd71d316
- https://git.kernel.org/stable/c/1e06710c43a090f14bb67714265a01cd1d7a37c5
- https://git.kernel.org/stable/c/221e3638feb8bc42143833c9a704fa89b6c366bb
- https://git.kernel.org/stable/c/2d6ae8b747fe55f54de4a4441d636974aa53f56a
- https://git.kernel.org/stable/c/5e8fdb6392d945d33fef959eab73f8c34bc0a63b
- https://git.kernel.org/stable/c/852c1f5f3119a38ee68e319bab10277fc1ab06b7
- https://git.kernel.org/stable/c/a725070701883fe62266ee6d2f31d67e6cdd31df
- https://git.kernel.org/stable/c/cd78b74031cbc94133965f1017deb822657fc1a6
- https://git.kernel.org/stable/c/f3c99c686e098300c246e5e8a1474133e3dacb05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49216.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49216
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
