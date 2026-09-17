# [H] iccDEV has a Heap-based Buffer Overflow in its CIccMBB::Validate() function

## Summary
Severity: High
Advisory: CVE-2026-21676
Aliases: GHSA-j5vv-p2hv-c392
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21676
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1 and below have a Heap-based Buffer Overflow in its CIccMBB::Validate function which checks tag data validity. This issue is fixed in version 2.3.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21676.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-j5vv-p2hv-c392
- https://nvd.nist.gov/vuln/detail/CVE-2026-21676
- https://github.com/InternationalColorConsortium/iccDEV/issues/215
- https://github.com/InternationalColorConsortium/iccDEV/commit/e4c38a67d06073b38d58580b0cfc78ca61005f84
