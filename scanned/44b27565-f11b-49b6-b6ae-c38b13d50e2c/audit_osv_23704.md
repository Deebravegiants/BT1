# [M] drm/amdgpu: Off by one in dm_dmub_outbox1_low_irq()

## Summary
Severity: Medium
Advisory: CVE-2022-49365
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49365
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Off by one in dm_dmub_outbox1_low_irq()

The > ARRAY_SIZE() should be >= ARRAY_SIZE() to prevent an out of bounds
access.

## References
- https://git.kernel.org/stable/c/607c5cd1a08e196d9f2bd3b25a8083ed27ad7ceb
- https://git.kernel.org/stable/c/a35faec3db0e13aac8ea720bc1a3503081dd5a3d
- https://git.kernel.org/stable/c/b0808b7a04157b3f56e919f27023fec37a075fad
- https://git.kernel.org/stable/c/ec9ec3bc08b18c5b1b2feafd306ea7c348013898
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49365.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49365
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
