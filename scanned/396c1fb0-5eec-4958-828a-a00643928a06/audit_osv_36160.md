# [H] iccDEV has heap-buffer-overflow vulnerability on IccTagXml()

## Summary
Severity: High
Advisory: CVE-2026-21678
Aliases: GHSA-9rp2-4c6g-hppf
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21678
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV is vulnerable to heap-buffer-overflow vulnerability in IccTagXml(). This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21678.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-9rp2-4c6g-hppf
- https://nvd.nist.gov/vuln/detail/CVE-2026-21678
- https://github.com/InternationalColorConsortium/iccDEV/issues/55
- https://github.com/InternationalColorConsortium/iccDEV/commit/c6c0f1cf45b48db94266132ccda5280a1a33569d
- https://github.com/InternationalColorConsortium/iccDEV/pull/219
