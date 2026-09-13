# [C] CVE-2026-51807

## Summary
Severity: Critical
Advisory: CVE-2026-51807
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-51807
Type: osv

## Details
Heap-based out-of-bounds write in j2k_precinct_subband::parse_packet_header() in OpenHTJ2K versions 0.18.3 and earlier (fixed in v0.18.4) caused by missing bounds validation before coding-pass lengths are written to j2k_codeblock::pass_length[128]. A crafted JPEG 2000 codestream containing malformed PPM packet headers can trigger a heap-based out-of-bounds write in j2k_precinct_subband::parse_packet_header() in source/core/coding/coding_units.cpp due to missing bounds validation for the j2k_codeblock::pass_length[128] array which can lead to heap corruption and process termination.

## References
- https://github.com/osamu620/OpenHTJ2K/blob/main/CHANGELOG
- https://github.com/osamu620/OpenHTJ2K/compare/0778b93...v0.18.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/51xxx/CVE-2026-51807.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-51807
- https://github.com/osamu620/OpenHTJ2K/commit/0778b93
- https://github.com/osamu620/OpenHTJ2K/releases
