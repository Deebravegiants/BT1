# [H] iccDEV vulnerable to Heap Buffer Overflow in CIccFileIO::Read8()

## Summary
Severity: High
Advisory: CVE-2026-25583
Aliases: GHSA-5ffg-r52h-fgw3
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25583
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.3, there is a heap buffer overflow vulnerability in CIccFileIO::Read8() when processing malformed ICC profile files via unchecked fread operation. This issue has been patched in version 2.3.1.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25583.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-5ffg-r52h-fgw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-25583
- https://github.com/InternationalColorConsortium/iccDEV/issues/558
- https://github.com/InternationalColorConsortium/iccDEV/commit/8a6df2d8dac1e971a18be66fa36e3a0d6584f919
- https://github.com/InternationalColorConsortium/iccDEV/pull/562
