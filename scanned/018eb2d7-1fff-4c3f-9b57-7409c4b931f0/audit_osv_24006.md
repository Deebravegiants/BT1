# [M] dmaengine: mv_xor_v2: Fix a resource leak in mv_xor_v2_remove()

## Summary
Severity: Medium
Advisory: CVE-2022-49861
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49861
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.334, >=4.10.0 <4.14.300, >=4.15.0 <4.19.267, >=4.16.0 <5.4.225, >=4.20.0 <5.10.155, >=5.5.0 <5.15.79, >=5.11.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: mv_xor_v2: Fix a resource leak in mv_xor_v2_remove()

A clk_prepare_enable() call in the probe is not balanced by a corresponding
clk_disable_unprepare() in the remove function.

Add the missing call.

## References
- https://git.kernel.org/stable/c/04f2cc56d80a1ac058045a7835c5bfd910f17863
- https://git.kernel.org/stable/c/081195d17a0c4c636da2b869bd5809d42e8cbb13
- https://git.kernel.org/stable/c/0b7ee3d50f32d277bf024b4ddb4de54da43a3025
- https://git.kernel.org/stable/c/1d84887327659c58a6637060ac8c50c3a952a163
- https://git.kernel.org/stable/c/20479886b40c0ed4864a5fc8490a1f6b70cccf1b
- https://git.kernel.org/stable/c/4b6641c3a2ba95ddcfecec263b4a5e572a4b0641
- https://git.kernel.org/stable/c/992e966caf57e00855edbd79f19d911809732a69
- https://git.kernel.org/stable/c/a1cb72e20a64a3c83f9b4ee993fbf97e4c1d7714
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49861.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49861
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
