# [M] iccDEV: NPD in CIccTagLut16::Write()

## Summary
Severity: Medium
Advisory: CVE-2026-34551
Aliases: GHSA-jmx9-9xmx-g57h
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34551
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a null-pointer dereference (NPD) in CIccTagLut16::Write() can be triggered when processing a crafted ICC profile (embedded in a TIFF and extracted during iccTiffDump). This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34551.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-jmx9-9xmx-g57h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34551
- https://github.com/InternationalColorConsortium/iccDEV/issues/702
- https://github.com/InternationalColorConsortium/iccDEV/pull/728
