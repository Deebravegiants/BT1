# [M] HDF5 H5T__ref_mem_setnull Heap Buffer Overflow

## Summary
Severity: Medium
Advisory: CVE-2026-29043
Aliases: GHSA-qm2m-5g5w-2277
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-29043
Type: osv

## Details
HDF5 is software for managing data. In 1.14.1-2 and earlier, an attacker who can control an h5 file parsed by HDF5 can trigger a write-based heap buffer overflow condition in the H5T__ref_mem_setnull method. This can lead to a denial-of-service condition, and potentially further issues such as remote code execution depending on the practical exploitability of the heap overflow against modern operating systems.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29043.json
- https://github.com/HDFGroup/hdf5/security/advisories/GHSA-qm2m-5g5w-2277
- https://nvd.nist.gov/vuln/detail/CVE-2026-29043
