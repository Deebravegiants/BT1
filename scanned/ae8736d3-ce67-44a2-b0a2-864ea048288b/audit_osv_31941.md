# [H] Revert "arm64: dts: qcom: sdm845: Affirm IDR0.CCTW on apps_smmu"

## Summary
Severity: High
Advisory: CVE-2025-22012
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/CVE-2025-22012
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "arm64: dts: qcom: sdm845: Affirm IDR0.CCTW on apps_smmu"

There are reports that the pagetable walker cache coherency is not a
given across the spectrum of SDM845/850 devices, leading to lock-ups
and resets. It works fine on some devices (like the Dragonboard 845c,
but not so much on the Lenovo Yoga C630).

This unfortunately looks like a fluke in firmware development, where
likely somewhere in the vast hypervisor stack, a change to accommodate
for this was only introduced after the initial software release (which
often serves as a baseline for products).

Revert the change to avoid additional guesswork around crashes.

This reverts commit 6b31a9744b8726c69bb0af290f8475a368a4b805.

## References
- https://git.kernel.org/stable/c/9e6e9fc90258a318d30b417bcccda908bb82ee9d
- https://git.kernel.org/stable/c/f00db31d235946853fb430de8c6aa1295efc8353
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22012.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22012
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
