# [H] wifi: mt76: mt7925: fix off by one in mt7925_load_clc()

## Summary
Severity: High
Advisory: CVE-2024-57990
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57990
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7925: fix off by one in mt7925_load_clc()

This comparison should be >= instead of > to prevent an out of bounds
read and write.

## References
- https://git.kernel.org/stable/c/08fa656c91fd5fdf47ba393795b9c0d1e97539ed
- https://git.kernel.org/stable/c/2d1628d32300e4f67ac0b7409cbfa7b912a8fe9d
- https://git.kernel.org/stable/c/d03b8fe1b518fc2ea2d82588e905f56d80cd64b2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57990.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57990
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
