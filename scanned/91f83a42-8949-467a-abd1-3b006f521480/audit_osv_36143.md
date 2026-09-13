# [H] iccDEV is Vulnerable to Denial of Service via Infinite Loop in CalcProfileID()

## Summary
Severity: High
Advisory: CVE-2026-21507
Aliases: GHSA-hgp5-r8m9-8qpj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21507
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1 and below have an infinite loop in the IccProfile.cpp function, CalcProfileID. This issue is fixed in version 2.3.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21507.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-hgp5-r8m9-8qpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-21507
- https://github.com/InternationalColorConsortium/iccDEV/issues/244
- https://github.com/InternationalColorConsortium/iccDEV/commit/3f3ce789d0d2b608c194ed172fa38943519dc198
