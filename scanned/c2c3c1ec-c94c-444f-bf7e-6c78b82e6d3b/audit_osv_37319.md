# [H] iccDEV has a heap-based buffer overflow in CIccCalculatorFunc::InitSelectOp()

## Summary
Severity: High
Advisory: CVE-2026-30979
Aliases: GHSA-8c76-67wr-hrp4
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30979
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a heap-based buffer overflow in CIccCalculatorFunc::InitSelectOp() triggered with local user interaction causing memory corruption/crash. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30979.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-8c76-67wr-hrp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-30979
- https://github.com/InternationalColorConsortium/iccDEV/issues/617
- https://github.com/InternationalColorConsortium/iccDEV/pull/622
