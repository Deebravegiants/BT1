# [M] MapServer has heap buffer overflow in SLD `Categorize` Threshold parsing

## Summary
Severity: Medium
Advisory: CVE-2026-33721
Aliases: GHSA-cv4m-mr84-fgjp
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33721
Type: osv

## Details
MapServer is a system for developing web-based GIS applications. Starting in version 4.2 and prior to version 8.6.1, a heap-buffer-overflow write in MapServer’s SLD (Styled Layer Descriptor) parser lets a remote, unauthenticated attacker crash the MapServer process by sending a crafted SLD with more than 100 Threshold elements inside a ColorMap/Categorize structure (commonly reachable via WMS GetMap with SLD_BODY). Version 8.6.1 patches the issue.

## References
- https://github.com/MapServer/MapServer/releases/tag/rel-8-6-1
- https://lists.debian.org/debian-lts-announce/2026/04/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33721.json
- https://github.com/MapServer/MapServer/security/advisories/GHSA-cv4m-mr84-fgjp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33721
