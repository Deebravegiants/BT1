# [H] iccDEV has a stack buffer overflow in CIccTagNum<(icTagTypeSignature)>::GetValues()

## Summary
Severity: High
Advisory: CVE-2026-30987
Aliases: GHSA-fj57-gfhq-rjqr
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30987
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a stack buffer overflow in CIccTagNum<>::GetValues() causing stack memory corruption or crash. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30987.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-fj57-gfhq-rjqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-30987
- https://github.com/InternationalColorConsortium/iccDEV/issues/618
- https://github.com/InternationalColorConsortium/iccDEV/pull/638
