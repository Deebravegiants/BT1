# [C] OpenEXR has integer overflow in DWA decoder outBufferEnd pointer arithmetic (missed variant of CVE-2026-34589)

## Summary
Severity: Critical
Advisory: CVE-2026-40250
Aliases: GHSA-m5qw-23x2-6phj
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40250
Type: osv

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. In versions 3.4.0 through 3.4.9, 3.3.0 through 3.3.9, and 3.2.0 through 3.2.7, `internal_dwa_compressor.h:1040` performs `chan->width * chan->bytes_per_element` in `int32` arithmetic without a `(size_t)` cast. This is the same overflow pattern fixed in other decoders by CVE-2026-34589/34588/34544, but this line was missed. Versions 3.4.10, 3.3.10, and 3.2.8 contain a fix that addresses `internal_dwa_compressor.h:1040`.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.2.8
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.10
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.10
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-m5qw-23x2-6phj
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40250.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40250
