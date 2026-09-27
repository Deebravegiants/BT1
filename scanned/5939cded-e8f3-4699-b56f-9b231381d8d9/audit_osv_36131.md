# [M] iccDEV has Type Confusion during XML Curve Serialization

## Summary
Severity: Medium
Advisory: CVE-2026-21493
Aliases: GHSA-p85g-f9q7-jmjx
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21493
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1.1 and below are vulnerable to Type Confusion in its CIccSingleSampledeCurveXml class during XML Curve Serialization. This issue is fixed in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21493.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-p85g-f9q7-jmjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-21493
- https://github.com/InternationalColorConsortium/iccDEV/issues/358
- https://github.com/InternationalColorConsortium/iccDEV/commit/7ff76d1471077172f9659de8d9536443eac7c48f
