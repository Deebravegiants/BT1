# [H] power: supply: gpio-charger: Fix set charge current limits

## Summary
Severity: High
Advisory: CVE-2024-57792
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57792
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.123, >=6.2.0 <6.6.69, >=6.7.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

power: supply: gpio-charger: Fix set charge current limits

Fix set charge current limits for devices which allow to set the lowest
charge current limit to be greater zero. If requested charge current limit
is below lowest limit, the index equals current_limit_map_size which leads
to accessing memory beyond allocated memory.

## References
- https://git.kernel.org/stable/c/13eb3cae1d8e23cce96c095abe34da8028c09ac5
- https://git.kernel.org/stable/c/6abbbd8286b6f944eecf3c74444c138590135211
- https://git.kernel.org/stable/c/afc6e39e824ad0e44b2af50a97885caec8d213d1
- https://git.kernel.org/stable/c/b29c7783ac1fe36d639c089cf471ac7a46df05f0
- https://git.kernel.org/stable/c/c3703d9340ca2820e1ac63256f4b423ea8559831
- https://git.kernel.org/stable/c/f6279a98db132da0cfff18712a1b06478c32007f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57792.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57792
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
