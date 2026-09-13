# [M] OpenEXR: Out-of-bounds read in HTJ2K decoder from unvalidated chunk header length (PLEN)

## Summary
Severity: Medium
Advisory: CVE-2026-65979
Aliases: GHSA-3j9c-j7c9-x293
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-65979
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. From version 3.4.0 through 3.4.12, the HTJ2K decoder parses a header-length field (PLEN) from a chunk's compressed data but never checks that this value fits within the available buffer before using it. When decoding, it advances the codestream pointer by the attacker-supplied header size and passes the resulting offset and remaining length to the OpenJPH memory-input path, so a crafted value pushes the pointer past the end of the buffer and causes an out-of-bounds read. Because this field comes straight from attacker-controlled EXR chunk data, the flaw is reachable during normal decoding of an untrusted file. This issue is fixed in version 3.4.13.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.13
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-3j9c-j7c9-x293
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65979.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65979
- https://github.com/AcademySoftwareFoundation/openexr/commit/c7af2d233b7b2a4452c11f26cf47584cc2b35721
