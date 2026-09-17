# [H] zlib 1.3.1.2 through 1.3.2 Heap Buffer Overflow via gz_vacate

## Summary
Severity: High
Advisory: CVE-2026-85091
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85091
Type: osv

## Details
zlib versions 1.3.1.2 through 1.3.2 contain a heap buffer overflow vulnerability in the gz_vacate() function when processing non-blocking gzwrite() operations with stale external buffer pointers. Attackers can trigger the overflow by calling gzprintf() or gzvprintf() after a write stall, causing an unchecked memmove() to write beyond the internal input buffer boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85091.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85091
- https://www.vulncheck.com/advisories/zlib-1.3.1.2-through-1.3.2-heap-buffer-overflow-via-gz-vacate
- https://github.com/madler/zlib
- https://github.com/madler/zlib/blob/v1.3.2/gzwrite.c#L393
- https://gist.github.com/thesmartshadow/e0b9481792afb7c31e86fee1ff084490
