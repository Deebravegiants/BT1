# [M] HTSlib CRAM decoder vulnerable to buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2026-31968
Aliases: GHSA-cgcm-c9r2-p57j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-31968
Type: osv

## Details
HTSlib is a library for reading and writing bioinformatics file formats. CRAM is a compressed format which stores DNA sequence alignment data using a variety of encodings and compression methods. For the `VARINT` and `CONST` encodings, incomplete validation of the context in which the encodings were used could result in up to eight bytes being written beyond the end of a heap allocation, or up to eight bytes being written to the location of a one byte variable on the stack, possibly causing the values to adjacent variables to change unexpectedly. Depending on the data stream this could result either in a heap buffer overflow or a stack overflow. If a user opens a file crafted to exploit this issue it could lead to the program crashing, overwriting of data structures on the heap or stack in ways not expected by the program, or changing the control flow of the program. It may be possible to use this to obtain arbitrary code execution. Versions 1.23.1, 1.22.2 and 1.21.1 include fixes for this issue. There is no workaround for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31968.json
- https://github.com/samtools/htslib/security/advisories/GHSA-cgcm-c9r2-p57j
- https://nvd.nist.gov/vuln/detail/CVE-2026-31968
- https://github.com/samtools/htslib/commit/0ec436796eca7b4ce7fcc9b77270c102da29bb2e
