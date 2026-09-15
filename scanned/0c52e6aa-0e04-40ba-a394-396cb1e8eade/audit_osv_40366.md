# [H] soc/tegra: cbb: Fix incorrect ARRAY_SIZE in fabric lookup tables

## Summary
Severity: High
Advisory: CVE-2026-53044
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53044
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc/tegra: cbb: Fix incorrect ARRAY_SIZE in fabric lookup tables

Fix incorrect ARRAY_SIZE usage in fabric lookup tables which could
cause out-of-bounds access during target timeout lookup.

## References
- https://git.kernel.org/stable/c/499f7e5ebbdd9ff0c4d532b1c432f8a61ff585b3
- https://git.kernel.org/stable/c/5c009a5f8bb3c81f2cfb511701ce571e3c8733cd
- https://git.kernel.org/stable/c/f46870b451f7583802ed26eec8b93e138840fcd9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53044.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53044
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
