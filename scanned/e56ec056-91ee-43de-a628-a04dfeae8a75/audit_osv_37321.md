# [M] iccDEV has a heap-buffer-overflow read in CIccXmlArrayType<>

## Summary
Severity: Medium
Advisory: CVE-2026-30981
Aliases: GHSA-pmcg-2h65-35h8
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30981
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a heap-buffer-overflow read in CIccXmlArrayType<>::DumpArray() causing out-of-bounds read and/or crash. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30981.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-pmcg-2h65-35h8
- https://nvd.nist.gov/vuln/detail/CVE-2026-30981
- https://github.com/InternationalColorConsortium/iccDEV/issues/627
- https://github.com/InternationalColorConsortium/iccDEV/pull/631
