# [M] iccDEV has a SEGV in CIccCLUT::Interp3d()

## Summary
Severity: Medium
Advisory: CVE-2026-31794
Aliases: GHSA-6jrq-wfqg-wv7w
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-31794
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a segmentation fault from invalid/wild pointer read in CIccCLUT::Interp3d() causing a denial of service. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31794.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-6jrq-wfqg-wv7w
- https://nvd.nist.gov/vuln/detail/CVE-2026-31794
- https://github.com/InternationalColorConsortium/iccDEV/issues/645
- https://github.com/InternationalColorConsortium/iccDEV/pull/653
