# [M] iccDEV has a SEGV in CIccCalculatorFunc::ApplySequence()

## Summary
Severity: Medium
Advisory: CVE-2026-31793
Aliases: GHSA-vgr5-3xqx-vcqx
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-31793
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a segmentation fault due to invalid/wild pointer read in CIccCalculatorFunc::ApplySequence() causing denial of service. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31793.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-vgr5-3xqx-vcqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-31793
- https://github.com/InternationalColorConsortium/iccDEV/issues/644
- https://github.com/InternationalColorConsortium/iccDEV/pull/652
