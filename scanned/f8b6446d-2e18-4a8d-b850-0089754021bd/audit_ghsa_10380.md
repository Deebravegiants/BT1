# [H] OpenEXR: Heap information disclosure in PXR24 decompression via unchecked decompressed size (undo_pxr24_impl)

## Summary
Severity: High
Advisory: GHSA-vc68-257w-m432
CVE: CVE-2026-34543
CWE: CWE-908
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-vc68-257w-m432
Type: github-advisory

## Affected
- PyPI: `openexr` — affected >=3.4.0 <3.4.8
- PyPI: `openexr` — affected >=3.3.0
- PyPI: `openexr` — affected >=3.2.0

## Details
### Summary
The PXR24 decompression function undo_pxr24_impl in OpenEXR (internal_pxr24.c) ignores the actual decompressed size (outSize) returned by exr_uncompress_buffer() and instead reads from the scratch buffer based solely on the expected size (uncompressed_size) derived from the header metadata.

Additionally, exr_uncompress_buffer() (compression.c:202) treats LIBDEFLATE_SHORT_OUTPUT (where the compressed stream decompresses to fewer bytes than expected) as a successful result rather than an error.

When these two issues are combined, an attacker can craft a PXR24 EXR file containing a valid but truncated zlib stream. As a result, the decoder reads uninitialized heap memory and incorporates it into the output pixel data.

### Details
This issue occurs due to the combination of two flaws.

1. compression.c:202–205 — LIBDEFLATE_SHORT_OUTPUT treated as success
```
else if (res == LIBDEFLATE_SHORT_OUTPUT)
{
    /* TODO: is this an error? */
    return EXR_ERR_SUCCESS;
}
```
libdeflate_zlib_decompress_ex() returns LIBDEFLATE_SHORT_OUTPUT when the compressed stream is successfully decompressed but the resulting output size is smaller than the provided output buffer size. In this case, the actual number of decompressed bytes is written to actual_out. However, the function does not treat this condition as an error and instead returns success.

2. internal_pxr24.c:279–287 — outSize return value ignored
```
rstat = exr_uncompress_buffer(
    decode->context, compressed_data, comp_buf_size,
    scratch_data, scratch_size, &outSize);   // outSize = actual bytes written

if (rstat != EXR_ERR_SUCCESS) return rstat;

// outSize is never referenced afterwards.
// The loop below reads the entire scratch_data buffer based on
// uncompressed_size (the header-derived expected size).
for (int y = 0; y < decode->chunk.height; ++y) { ... }
```
After exr_uncompress_buffer() returns success, the code does not verify whether the actual decompressed size (outSize) matches the expected size (uncompressed_size). The subsequent byte-plane reconstruction loop reads from the scratch buffer up to uncompressed_size bytes. As a result, the region between outSize and uncompressed_size consists of uninitialized heap memory, which is then read by the decoder.

**Affected component**
- src/lib/OpenEXRCore/internal_pxr24.c — undo_pxr24_impl() (line 261–399)
- src/lib/OpenEXRCore/compression.c — exr_uncompress_buffer() (line 202–205)

### PoC
Please refer to the atta
[poc.zip](https://github.com/user-attachments/files/26002361/poc.zip)
ched archive file and proceed after extracting it.

1. git clone https://github.com/AcademySoftwareFoundation/openexr.git
2. mv poc openexr/
3. cd openexr
4. docker build -f poc/Dockerfile -t pxr24-poc .
5. docker run --rm pxr24-poc

<img width="858" height="155" alt="스크린샷 2026-03-15 오후 4 38 18" src="https://github.com/user-attachments/assets/ded9eab6-9b92-40f7-9a0d-7b00db7e6088" />


### Impact
* Sensitive information from heap memory may be leaked through the decoded pixel data (information disclosure).
Trigger Condition: Occurs under default settings; simply reading a malicious EXR file is sufficient to trigger the issue, without any user interaction.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-vc68-257w-m432
- https://nvd.nist.gov/vuln/detail/CVE-2026-34543
- https://github.com/AcademySoftwareFoundation/openexr/commit/5f6d0aaa9e43802917af7db90f181e88e083d3b8
- https://github.com/AcademySoftwareFoundation/openexr
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.8
