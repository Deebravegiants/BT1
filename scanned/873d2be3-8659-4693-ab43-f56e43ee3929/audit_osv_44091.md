# [M] CVE-2026-79522

## Summary
Severity: Medium
Advisory: CVE-2026-79522
CVSS: 6.5 (CVSS:3.1/AC:L/AV:N/A:H/C:N/I:N/PR:N/S:U/UI:R)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-79522
Type: osv

## Details
An out-of-bounds read in the gf_dm_get_chunk_data function (src/utils/downloader.c) of GPAC v26.07.0 allows attackers to cause a Denial of Service (DoS) via sending a crafted HTTP request. Fixed in 2fd5a06ab226767900fd86edb5a1e8bfc1010640.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79522.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-79522
- https://github.com/gpac/gpac/issues/3861
- https://github.com/gpac/gpac/commit/2fd5a06ab226767900fd86edb5a1e8bfc1010640
