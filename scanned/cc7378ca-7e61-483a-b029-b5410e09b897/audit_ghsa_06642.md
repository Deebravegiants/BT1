# [M] adawolfa/isdoc: Uncontrolled resource consumption (decompression bomb) when reading untrusted ISDOCX or PDF files

## Summary
Severity: Medium
Advisory: GHSA-xg43-5579-qw6v
CWE: CWE-400, CWE-409
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-xg43-5579-qw6v
Type: github-advisory

## Affected
- Packagist: `adawolfa/isdoc` — affected >=1.6.0 <1.6.1
- Packagist: `adawolfa/isdoc` — affected >=1.5.0 <1.5.1
- Packagist: `adawolfa/isdoc` — affected >=1.4.0 <1.4.3
- Packagist: `adawolfa/isdoc` — affected >=0

## Details
### Impact

`adawolfa/isdoc` reads ISDOC invoices from ISDOCX (ZIP) archives and from PDF files with embedded ISDOC documents and supplements. Affected versions inflate ZIP entries and read embedded files **without validating their uncompressed size**, so a small crafted file can amplify into gigabytes:

- **ISDOCX decompression bomb** — `getFromName()` inflates the ISDOC document and binary supplements with no size cap.
- **`saveTo()` disk-fill** — the supplement copy loop writes inflated bytes to disk with no running byte budget, so a bomb can exhaust disk even if the central-directory size is under-reported.
- **PDF embedded files** — an embedded file whose declared `Length` is enormous is read and digested with no upper bound.

Exploitation requires the application to parse an attacker-supplied `.isdocx` or `.pdf` (the typical use is generating files or parsing files from trusted vendors, so a user must be induced to process a malicious file). When that happens the process can be driven to exhaust memory or disk, causing denial of service. There is **no confidentiality or integrity impact** — availability only.

### Patches

Fixed in **1.4.3**, **1.5.1**, **1.6.1** and **2.0.0**. The readers now:

- read the uncompressed size from the ZIP central directory (`statName()`) and reject entries over a cap **before inflating** — 256 KB (`DocumentSizeLimit`) for the ISDOC document, 32 MB (`SizeLimit`) for supplements;
- enforce a running byte budget in `saveTo()` and unlink the partial file on overflow;
- reject PDF-embedded files whose declared `Length` exceeds 256 MB before reading or digesting them.

New exceptions `ReaderException::zipEntryTooLarge()`, `SupplementException::supplementTooLarge()` and `ReaderException::pdfSupplementTooLarge()` surface the rejection.

### Unsupported versions

Versions **before 1.4.0** (the 1.0–1.3 lines) are also affected and will **not** receive a fix, because they target end-of-life PHP. Users on those lines should upgrade to a maintained release — 1.4.3, 1.5.1, 1.6.1, or 2.0.0.

### Workarounds

No code-level workaround exists in affected versions; upgrading is the fix. As mitigation, restrict parsing to trusted input, or enforce an external size / decompression limit (validate ZIP entry sizes, cap process memory) before handing files to the library.

### Resources

- Decompression-bomb fix: commit [`935fb2a`](https://github.com/adawolfa/isdoc/commit/935fb2aa41ceddfcf43174a61a36ec620611a105) (backported, released as 1.4.3 / 1.5.1 / 1.6.1) and [`02a1012`](https://github.com/adawolfa/isdoc/commit/02a10123a3d5fd92950b8e4952959317c0a18952) (master, released as 2.0.0).
- CWE-409 (Improper Handling of Highly Compressed Data), CWE-400 (Uncontrolled Resource Consumption).

## References
- https://github.com/adawolfa/isdoc/security/advisories/GHSA-xg43-5579-qw6v
- https://github.com/adawolfa/isdoc/commit/02a10123a3d5fd92950b8e4952959317c0a18952
- https://github.com/adawolfa/isdoc/commit/935fb2aa41ceddfcf43174a61a36ec620611a105
- https://github.com/adawolfa/isdoc
