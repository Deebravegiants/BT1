# [H] OpenEXR has a misaligned write in LossyDctDecoder_execute leading to undefined behavior (DWA/DWAB decompression)

## Summary
Severity: High
Advisory: CVE-2026-34379
Aliases: GHSA-w88v-vqhq-5p24
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-34379
Type: osv

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From 3.2.0 to before 3.2.7, 3.3.9, and 3.4.9, a misaligned memory write vulnerability exists in LossyDctDecoder_execute() in src/lib/OpenEXRCore/internal_dwa_decoder.h:749. When decoding a DWA or DWAB-compressed EXR file containing a FLOAT-type channel, the decoder performs an in-place HALF→FLOAT conversion by casting an unaligned uint8_t * row pointer to float * and writing through it. Because the row buffer may not be 4-byte aligned, this constitutes undefined behavior under the C standard and crashes immediately on architectures that enforce alignment (ARM, RISC-V, etc.). On x86 it is silently tolerated at runtime but remains exploitable via compiler optimizations that assume aligned access. This vulnerability is fixed in 3.2.7, 3.3.9, and 3.4.9.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.2.7
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.9
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.9
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34379.json
- https://access.redhat.com/security/cve/CVE-2026-34379
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-w88v-vqhq-5p24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34379.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34379
- https://bugzilla.redhat.com/show_bug.cgi?id=2455402
