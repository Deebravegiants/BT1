# [M] HTSlib BGZF index file reader has a heap buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2026-31970
Aliases: GHSA-p345-84hx-fq6q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-31970
Type: osv

## Details
HTSlib is a library for reading and writing bioinformatics file formats. GZI files are used to index block-compressed GZIP [BGZF] files.  In the GZI loading function, `bgzf_index_load_hfile()`, it was possible to trigger an integer overflow, leading to an under- or zero-sized buffer being allocated to store the index.  Sixteen zero bytes would then be written to this buffer, and, depending on the result of the overflow the rest of the file may also be loaded into the buffer as well.  If the function did attempt to load the data, it would eventually fail due to not reading the expected number of records, and then try to free the overflowed heap buffer. Exploiting this bug causes a heap buffer overflow. If a user opens a file crafted to exploit this issue, it could lead to the program crashing, or overwriting of data and heap structures in ways not expected by the program.  It may be possible to use this to obtain arbitrary code execution. Versions 1.23.1, 1.22.2 and 1.21.1 include fixes for this issue. The easiest work-around is to discard any `.gzi` index files from untrusted sources, and use the `bgzip -r` option to recreate them.

## References
- http://www.openwall.com/lists/oss-security/2026/03/18/9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31970.json
- https://github.com/samtools/htslib/security/advisories/GHSA-p345-84hx-fq6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-31970
- https://github.com/samtools/htslib/commit/6dd0d7d0e9e7e2e173a28969e624db8bc8bb5828
