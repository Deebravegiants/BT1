# [C] nvme: fix FDP fdpcidx bounds check

## Summary
Severity: Critical
Advisory: CVE-2026-74361
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74361
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme: fix FDP fdpcidx bounds check

The fdpcidx bounds check sets n = NUMFDPC + 1 but used > instead of >=,
incorrectly accepting fdp_idx when it equals n (i.e. NUMFDPC + 1).

## References
- https://git.kernel.org/stable/c/0967074f6830718fd2597404ef119bddd0dbfd00
- https://git.kernel.org/stable/c/5d0e7d2af884b91329235abb16652ae4eead8079
- https://git.kernel.org/stable/c/5e406928404d67a8da8aa3ae21732e1ea1a04118
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74361.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74361
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
