# [M] arm64: errata: Add Cortex-A520 speculative unprivileged load workaround

## Summary
Severity: Medium
Advisory: CVE-2023-52481
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-52481
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <6.1.57, >=6.2.0 <6.5.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: errata: Add Cortex-A520 speculative unprivileged load workaround

Implement the workaround for ARM Cortex-A520 erratum 2966298. On an
affected Cortex-A520 core, a speculatively executed unprivileged load
might leak data from a privileged load via a cache side channel. The
issue only exists for loads within a translation regime with the same
translation (e.g. same ASID and VMID). Therefore, the issue only affects
the return to EL0.

The workaround is to execute a TLBI before returning to EL0 after all
loads of privileged data. A non-shareable TLBI to any address is
sufficient.

The workaround isn't necessary if page table isolation (KPTI) is
enabled, but for simplicity it will be. Page table isolation should
normally be disabled for Cortex-A520 as it supports the CSV3 feature
and the E0PD feature (used when KASLR is enabled).

## References
- https://git.kernel.org/stable/c/32b0a4ffcaea44a00a61e40c0d1bcc50362aee25
- https://git.kernel.org/stable/c/471470bc7052d28ce125901877dd10e4c048e513
- https://git.kernel.org/stable/c/6e3ae2927b432a3b7c8374f14dbc1bd9ebe4372c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52481.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52481
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
