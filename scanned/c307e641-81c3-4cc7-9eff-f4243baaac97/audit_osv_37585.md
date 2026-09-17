# [M] HTSlib CRAM reader has heap buffer overflow due to improper validation of input

## Summary
Severity: Medium
Advisory: CVE-2026-31962
Aliases: GHSA-xxmp-v7h3-gpwp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-31962
Type: osv

## Details
HTSlib is a library for reading and writing bioinformatics file formats. CRAM is a compressed format which stores DNA sequence alignment data. While most alignment records store DNA sequence and quality values, the format also allows them to omit this data in certain cases to save space. Due to some quirks of the CRAM format, it is necessary to handle these records carefully as they will actually store data that needs to be consumed and then discarded. Unfortunately the `cram_decode_seq()` did not handle this correctly in some cases. Where this happened it could result in reading a single byte from beyond the end of a heap allocation, followed by writing a single attacker-controlled byte to the same location. Exploiting this bug causes a heap buffer overflow. If a user opens a file crafted to exploit this issue, it could lead to the program crashing, or overwriting of data and heap structures in ways not expected by the program.  It may be possible to use this to obtain arbitrary code execution. Versions 1.23.1, 1.22.2 and 1.21.1 include fixes for this issue. There is no workaround for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31962.json
- https://github.com/samtools/htslib/security/advisories/GHSA-xxmp-v7h3-gpwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-31962
- https://github.com/samtools/htslib/commit/d799b54c6401879187bba4741be83ff590ac73e3
