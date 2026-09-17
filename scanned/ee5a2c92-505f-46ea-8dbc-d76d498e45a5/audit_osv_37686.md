# [M] libheif has a Heap OOB Read/SEGV Crash via Zero samples_per_chunk

## Summary
Severity: Medium
Advisory: CVE-2026-32738
Aliases: GHSA-7f2h-cmpf-v9ww
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-32738
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In versions 1.21.2 and below, a crafted 792-byte HEIF sequence file with samples_per_chunk=0 in the stsc box causes an unsigned integer underflow in the Chunk constructor (m_last_sample = 0 + 0 - 1 = UINT32_MAX), mapping all samples to an empty chunk and resulting in a denial of service. When any sample is accessed, the library reads from index 0 of an empty std::vector, causing a guaranteed SEGV (null-page read). The file parses successfully without producing an error; the crash occurs on the first frame access. This issue has been fixed in version 1.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32738.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-7f2h-cmpf-v9ww
- https://nvd.nist.gov/vuln/detail/CVE-2026-32738
