# [M] iccDEV has Out-of-bounds Read and Integer Underflow (Wrap or Wraparound)

## Summary
Severity: Medium
Advisory: CVE-2026-21489
Aliases: GHSA-ph89-6q5h-wfw5
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21489
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1.1 and below have Out-of-bounds Read and Integer Underflow (Wrap or Wraparound) vulnerabilities in its CIccCalculatorFunc::SequenceNeedTempReset function. This issue is fixed in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21489.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-ph89-6q5h-wfw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-21489
- https://github.com/InternationalColorConsortium/iccDEV/commit/cfabfe52c9c7eb0481b62c8aad56580bb11efdad
