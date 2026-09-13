# [M] iccDEV has a heap out-of-bounds read in CIccCalculatorFunc::ApplySequence()

## Summary
Severity: Medium
Advisory: CVE-2026-30984
Aliases: GHSA-g9w6-5xm9-v5xj
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30984
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a heap out-of-bounds read in CIccCalculatorFunc::ApplySequence() causing an application crash. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30984.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-g9w6-5xm9-v5xj
- https://nvd.nist.gov/vuln/detail/CVE-2026-30984
- https://github.com/InternationalColorConsortium/iccDEV/issues/623
- https://github.com/InternationalColorConsortium/iccDEV/pull/635
