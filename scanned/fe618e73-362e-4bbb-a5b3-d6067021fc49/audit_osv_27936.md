# [H] irqchip/gic-v3-its: Restore quirk probing for ACPI-based systems

## Summary
Severity: High
Advisory: CVE-2024-26823
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26823
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/gic-v3-its: Restore quirk probing for ACPI-based systems

While refactoring the way the ITSs are probed, the handling of quirks
applicable to ACPI-based platforms was lost. As a result, systems such as
HIP07 lose their GICv4 functionnality, and some other may even fail to
boot, unless they are configured to boot with DT.

Move the enabling of quirks into its_probe_one(), making it common to all
firmware implementations.

## References
- https://git.kernel.org/stable/c/4c60c611441f1f1e5de8e00e98ee5a4970778a00
- https://git.kernel.org/stable/c/8b02da04ad978827e5ccd675acf170198f747a7a
- https://git.kernel.org/stable/c/91a80fff3eeed928b6fba21271f6a9719b22a5d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26823.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26823
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
