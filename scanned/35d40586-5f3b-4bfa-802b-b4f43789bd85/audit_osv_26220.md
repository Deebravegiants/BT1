# [M] arm64: dts: qcom: sdm845-db845c: Mark cont splash memory region as reserved

## Summary
Severity: Medium
Advisory: CVE-2023-52561
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52561
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.1.56, >=6.2.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: dts: qcom: sdm845-db845c: Mark cont splash memory region as reserved

Adding a reserved memory region for the framebuffer memory
(the splash memory region set up by the bootloader).

It fixes a kernel panic (arm-smmu: Unhandled context fault
at this particular memory region) reported on DB845c running
v5.10.y.

## References
- https://git.kernel.org/stable/c/110e70fccce4f22b53986ae797d665ffb1950aa6
- https://git.kernel.org/stable/c/82dacd0ca0d9640723824026d6fdf773c02de1d2
- https://git.kernel.org/stable/c/dc1ab6577475b0460ba4261cd9caec37bd62ca0b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52561.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52561
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
