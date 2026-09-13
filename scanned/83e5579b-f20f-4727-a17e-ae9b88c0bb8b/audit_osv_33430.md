# [H] ASoC: Intel: avs: Disable periods-elapsed work when closing PCM

## Summary
Severity: High
Advisory: CVE-2025-40344
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-40344
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: Intel: avs: Disable periods-elapsed work when closing PCM

avs_dai_fe_shutdown() handles the shutdown procedure for HOST HDAudio
stream while period-elapsed work services its IRQs. As the former
frees the DAI's private context, these two operations shall be
synchronized to avoid slab-use-after-free or worse errors.

## References
- https://git.kernel.org/stable/c/845f716dc5f354c719f6fda35048b6c2eca99331
- https://git.kernel.org/stable/c/b41fca4aa60be896ba8a81b57aac5dcc6eee66c0
- https://git.kernel.org/stable/c/ca6d2b7aca778afbf8c0c4b330d10cb228c14052
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40344.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40344
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
