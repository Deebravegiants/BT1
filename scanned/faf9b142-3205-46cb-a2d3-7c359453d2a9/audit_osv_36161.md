# [H] iccDEV has heap-buffer-overflow vulnerability in CIccLocalizedUnicode::GetText()

## Summary
Severity: High
Advisory: CVE-2026-21679
Aliases: GHSA-h4wg-473g-p5wc
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21679
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV is vulnerable to heap-buffer-overflow in CIccLocalizedUnicode::GetText(). This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21679.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-h4wg-473g-p5wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-21679
- https://github.com/InternationalColorConsortium/iccDEV/issues/328
- https://github.com/InternationalColorConsortium/iccDEV/commit/2eb25ab95f0db7664ec3850390b6f89e302e7039
- https://github.com/InternationalColorConsortium/iccDEV/pull/329
