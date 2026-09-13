# [M] platform/x86/amd/pmc: Detect when STB is not available

## Summary
Severity: Medium
Advisory: CVE-2024-53072
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53072
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86/amd/pmc: Detect when STB is not available

Loading the amd_pmc module as:

    amd_pmc enable_stb=1

...can result in the following messages in the kernel ring buffer:

    amd_pmc AMDI0009:00: SMU cmd failed. err: 0xff
    ioremap on RAM at 0x0000000000000000 - 0x0000000000ffffff
    WARNING: CPU: 10 PID: 2151 at arch/x86/mm/ioremap.c:217 __ioremap_caller+0x2cd/0x340

Further debugging reveals that this occurs when the requests for
S2D_PHYS_ADDR_LOW and S2D_PHYS_ADDR_HIGH return a value of 0,
indicating that the STB is inaccessible. To prevent the ioremap
warning and provide clarity to the user, handle the invalid address
and display an error message.

## References
- https://git.kernel.org/stable/c/67ff30e24a0466bdd5be1d0b84385ec3c85fdacd
- https://git.kernel.org/stable/c/7a3ed3f125292bc3398e04d10108124250892e3f
- https://git.kernel.org/stable/c/a50863dd1f92d43c975ab2ecc3476617fe98a66e
- https://git.kernel.org/stable/c/bceec87a73804bb4c33b9a6c96e2d27cd893a801
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53072.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53072
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
