# [M] OpenEXR: Integer overflow in the HTJ2K decoder leads to heap-buffer-overflow

## Summary
Severity: Medium
Advisory: CVE-2026-44663
Aliases: GHSA-777r-f9x8-7r84
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-44663
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. In versions 3.4.0 through 3.4.11, an integer overflow in ht_undo_impl() in src/lib/OpenEXRCore/internal_ht.cpp leads to a heap-buffer overflow when decoding a crafted HTJ2K-compressed EXR file. decode->channels[i].width (int32_t) is multiplied by bytes_per_element in 32-bit signed arithmetic. With large widths (e.g., >= 536870912 for FLOAT data), this overflows, producing a corrupted offset that is later used for pointer arithmetic and can cause a heap out-of-bounds write. The same unchecked multiplication pattern appears in two other HTJ2K paths (bytes-per-line accumulation and pixel-line pointer advancement). As with related CVE-2026-34378 through CVE-2026-34589 fixes in other codecs, validating only after the multiplication is too late because the value may already be overflowed. This issue has been fixed in version 3.4.12.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.12
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-777r-f9x8-7r84
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44663.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-44663
