# [M] iccDEV: DoS in CIccCLUT::Iterate() & CIccMBB::Describe()

## Summary
Severity: Medium
Advisory: CVE-2026-34553
Aliases: GHSA-5r4q-77w5-3q3h
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34553
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, there is a defect in LUT dump/iteration logic affecting CIccCLUT::Iterate() and output produced by CIccMBB::Describe() (via CLUT dumping). This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34553.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-5r4q-77w5-3q3h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34553
- https://github.com/InternationalColorConsortium/iccDEV/issues/704
- https://github.com/InternationalColorConsortium/iccDEV/pull/737
