# [M] NanaZip: Heap buffer-overflow read in NanaZip LVM metadata CRC check

## Summary
Severity: Medium
Advisory: CVE-2026-47224
Aliases: GHSA-qcgf-c2vp-fwjr
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47224
Type: osv

## Details
NanaZip is the 7-Zip derivative intended for the modern Windows experience. From version 3.0.1000.0 to before version 6.0.1698.0, a heap buffer-overflow read exists in the LVM2 physical-volume metadata parser in NanaZip (via the upstream 7-Zip LvmHandler). The vulnerability is triggered when opening a crafted LVM disk image. This issue has been patched in stable version 6.0.1698.0 and preview version 6.5.1742.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47224.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-qcgf-c2vp-fwjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-47224
