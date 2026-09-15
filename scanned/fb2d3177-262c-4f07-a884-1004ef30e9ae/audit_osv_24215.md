# [M] wifi: mt76: mt7921: resource leaks at mt7921_check_offload_capability()

## Summary
Severity: Medium
Advisory: CVE-2022-50424
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2022-50424
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7921: resource leaks at mt7921_check_offload_capability()

Fixed coverity issue with resource leaks at variable "fw" going out of
scope leaks the storage it points to mt7921_check_offload_capability().

Addresses-Coverity-ID: 1527806 ("Resource leaks")

## References
- https://git.kernel.org/stable/c/47180ecf4541146836c5307c1d5526f8ac6a5a6d
- https://git.kernel.org/stable/c/ead3cffd7510dc635d84cd4ea9dd1974fcb69a35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50424.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50424
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
