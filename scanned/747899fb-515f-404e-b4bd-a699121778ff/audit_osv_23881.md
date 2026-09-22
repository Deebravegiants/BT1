# [M] ASoC: rt711-sdca: fix kernel NULL pointer dereference when IO error

## Summary
Severity: Medium
Advisory: CVE-2022-49615
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49615
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: rt711-sdca: fix kernel NULL pointer dereference when IO error

The initial settings will be written before the codec probe function.
But, the rt711->component doesn't be assigned yet.
If IO error happened during initial settings operations, it will cause the kernel panic.
This patch changed component->dev to slave->dev to fix this issue.

## References
- https://git.kernel.org/stable/c/1df793d479bef546569fc2e409ff8bb3f0fb8e99
- https://git.kernel.org/stable/c/269be8b2907378adf72d7347cfa43ef230351a06
- https://git.kernel.org/stable/c/7bb71133cae88d3003a3490b97864af76533072b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49615.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49615
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
