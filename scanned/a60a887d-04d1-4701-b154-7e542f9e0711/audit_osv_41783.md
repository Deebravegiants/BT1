# [H] wifi: mt76: mt7996: Clear wcid pointer in mt7996_mac_sta_deinit_link()

## Summary
Severity: High
Advisory: CVE-2026-63866
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63866
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7996: Clear wcid pointer in mt7996_mac_sta_deinit_link()

Clear WCID pointer removing the sta link in mt7996_mac_sta_deinit_link
routine.

## References
- https://git.kernel.org/stable/c/455a48685feebf2d9c1656caad77f9ba1da7b06e
- https://git.kernel.org/stable/c/88973240dc7c976dd320b36a9e6d925c9be083ae
- https://git.kernel.org/stable/c/c575459b485c47615491b1fd29f04b43fdc3da56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63866.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63866
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
