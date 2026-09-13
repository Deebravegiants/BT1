# [M] regulator: pfuze100: Fix refcount leak in pfuze_parse_regulators_dt

## Summary
Severity: Medium
Advisory: CVE-2022-49481
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49481
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: pfuze100: Fix refcount leak in pfuze_parse_regulators_dt

of_node_get() returns a node with refcount incremented.
Calling of_node_put() to drop the reference when not needed anymore.

## References
- https://git.kernel.org/stable/c/0be5d9da5743b9825a95baec85a67500b2c1d362
- https://git.kernel.org/stable/c/49d785baeb91568332197be356d138e5e59c7ddb
- https://git.kernel.org/stable/c/56ab0c01027492cd161c64148e1dc892c56887ad
- https://git.kernel.org/stable/c/671be14fc31374b1a10a3abd93db6a8480838fc9
- https://git.kernel.org/stable/c/6ca675f4abbc74bc991d154a1ecc8b384dc2aae4
- https://git.kernel.org/stable/c/984cfef0675ed7398814e14af2c5323911723e1c
- https://git.kernel.org/stable/c/9f564e29a51210a49df3d925117777c157a17d6d
- https://git.kernel.org/stable/c/afaa7b933ef00a2d3262f4d1252087613fb5c06d
- https://git.kernel.org/stable/c/b74c0dd9179d21b7260260e075d597b23970100c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49481.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49481
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
