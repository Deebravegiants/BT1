# [M] CVE-2021-47067

## Summary
Severity: Medium
Advisory: CVE-2021-47067
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47067
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc/tegra: regulators: Fix locking up when voltage-spread is out of range

Fix voltage coupler lockup which happens when voltage-spread is out
of range due to a bug in the code. The max-spread requirement shall be
accounted when CPU regulator doesn't have consumers. This problem is
observed on Tegra30 Ouya game console once system-wide DVFS is enabled
in a device-tree.

## References
- https://git.kernel.org/stable/c/ef85bb582c41524e9e68dfdbde48e519dac4ab3d
- https://git.kernel.org/stable/c/ff39adf5d31c72025bba799aec69c5c86d81d549
- https://git.kernel.org/stable/c/a1ad124c836816fac8bd5e461d36eaf33cee4e24
- https://git.kernel.org/stable/c/dc4452867200fa94589b382740952b58aa1c3e6c
