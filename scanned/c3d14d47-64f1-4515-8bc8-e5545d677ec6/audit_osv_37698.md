# [M] mackron / dr_libs dr_flac.h Excessive Memory Allocation in PICTURE Metadata Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-32836
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-32836
Type: osv

## Details
dr_libs dr_flac.h version 0.13.3 and earlier (fixed in commits fefced4, 4f5a4cd, and 663239a) contain an uncontrolled memory allocation vulnerability in drflac__read_and_decode_metadata() that allows attackers to trigger excessive memory allocation by supplying crafted PICTURE metadata blocks. Attackers can exploit attacker-controlled mimeLength and descriptionLength fields to cause denial of service through memory exhaustion when processing FLAC streams with metadata callbacks.

## References
- https://github.com/mackron/dr_libs/blob/master/dr_flac.h
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32836.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-32836
- https://www.vulncheck.com/advisories/mackron-dr-libs-excessive-memory-allocation-in-picture-metadata-parsing
- https://github.com/mackron/dr_libs/issues/298
- https://github.com/mackron/dr_libs/commit/4f5a4cd3b57564d969443c580c75857e039f100a
- https://github.com/mackron/dr_libs/commit/663239a3d0460c33bd5b6e5166edcb404e3df676
- https://github.com/mackron/dr_libs/commit/fefced4a64adfb1a68a2d31d882366e56096dee8
