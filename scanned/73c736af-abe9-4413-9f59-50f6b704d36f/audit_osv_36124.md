# [H] Use After Free and Heap-based Buffer Overflow and Integer Overflow or Wraparound and Out-of-bounds Write in iccDEV

## Summary
Severity: High
Advisory: CVE-2026-21486
Aliases: GHSA-mg98-j5q2-674w
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21486
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1.1 and below contain Use After Free, Heap-based Buffer Overflow and Integer Overflow or Wraparound and Out-of-bounds Write vulnerabilities in its CIccSparseMatrix::CIccSparseMatrix function. This issue is fixed in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21486.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-mg98-j5q2-674w
- https://nvd.nist.gov/vuln/detail/CVE-2026-21486
- https://github.com/InternationalColorConsortium/iccDEV/commit/1ab7363f38a20089934d3410c88f714eea392bf5
