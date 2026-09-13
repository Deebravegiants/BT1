# [M] HTSlib CRAM decoder has a heap buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2026-31969
Aliases: GHSA-q4cj-f4h5-fqgc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-31969
Type: osv

## Details
HTSlib is a library for reading and writing bioinformatics file formats. CRAM is a compressed format which stores DNA sequence alignment data using a variety of encodings and compression methods.  When reading data encoded using the `BYTE_ARRAY_STOP` method, an out-by-one error in the `cram_byte_array_stop_decode_char()` function check for a full output buffer could result in a single attacker-controlled byte being written beyond the end of a heap allocation. Exploiting this bug causes a heap buffer overflow. If a user opens a file crafted to exploit this issue, it could lead to the program crashing, or overwriting of data and heap structures in ways not expected by the program.  It may be possible to use this to obtain arbitrary code execution. Versions 1.23.1, 1.22.2 and 1.21.1 include fixes for this issue. There is no workaround for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31969.json
- https://github.com/samtools/htslib/security/advisories/GHSA-q4cj-f4h5-fqgc
- https://nvd.nist.gov/vuln/detail/CVE-2026-31969
- https://github.com/samtools/htslib/commit/88cdf69e4b83bb550ab4f6f7134892c2ad1978f4
