# [M] netdevsim: prevent bad user input in nsim_dev_health_break_write()

## Summary
Severity: Medium
Advisory: CVE-2024-56716
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56716
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.122, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netdevsim: prevent bad user input in nsim_dev_health_break_write()

If either a zero count or a large one is provided, kernel can crash.

## References
- https://git.kernel.org/stable/c/470c5ecbac2f19b1cdee2a6ce8d5650c3295c94b
- https://git.kernel.org/stable/c/81bdfcd6e6a998e219c9dd49ec7291c2e0594bbc
- https://git.kernel.org/stable/c/8e9ef6bdf71bf25f4735e0230ce1919de8985835
- https://git.kernel.org/stable/c/b3a6daaf7cfb2de37b89fd7a5a2ad4ea9aa3e181
- https://git.kernel.org/stable/c/d10321be26ff9e9e912697e9e8448099654ff561
- https://git.kernel.org/stable/c/ee76746387f6233bdfa93d7406990f923641568f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56716.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56716
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
