# [H] OpenEXR Heap-Based Buffer Overflow in Deep Scanline Parsing via Forged Unpacked Size

## Summary
Severity: High
Advisory: GHSA-h45x-qhg2-q375
CVE: CVE-2025-48071
CWE: CWE-122
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-h45x-qhg2-q375
Type: github-advisory

## Affected
- PyPI: `OpenEXR` — affected >=3.3.0 <3.3.3

## Details
### Summary

The OpenEXRCore code is vulnerable to a heap-based buffer overflow during a write operation when decompressing ZIPS-packed deep scan-line EXR files with a maliciously forged chunk header.

### Details
When parsing `STORAGE_DEEP_SCANLINE` chunks from an EXR file, the following code (from `src/lib/OpenEXRCore/chunk.c`) is used to extract the chunk information:

```cpp

if (part->storage_mode == EXR_STORAGE_DEEP_SCANLINE)
// SNIP...
        cinfo->sample_count_data_offset = dataoff;
        cinfo->sample_count_table_size  = (uint64_t) ddata[0];
        cinfo->data_offset              = dataoff + (uint64_t) ddata[0];
        cinfo->packed_size              = (uint64_t) ddata[1];
        cinfo->unpacked_size            = (uint64_t) ddata[2];
// SNIP...
```

By storing this information, the code that will later decompress and reconstruct the chunk bytes, will know how much space the uncompressed data will occupy.

This size is carried along in the chain of decoding/decompression until the `undo_zip_impl` function in `src/lib/OpenEXRCore/internal_zip.c`:

```cpp
static exr_result_t
undo_zip_impl (
    exr_decode_pipeline_t* decode,
    const void*            compressed_data,
    uint64_t               comp_buf_size,
    void*                  uncompressed_data,
    uint64_t               uncompressed_size,
    void*                  scratch_data,
    uint64_t               scratch_size)
{
    size_t       actual_out_bytes;
    exr_result_t res;

    if (scratch_size < uncompressed_size) return EXR_ERR_INVALID_ARGUMENT;

    res = exr_uncompress_buffer (
        decode->context,
        compressed_data,
        comp_buf_size,
        scratch_data,
        scratch_size,
        &actual_out_bytes);

    if (res == EXR_ERR_SUCCESS)
    {
        decode->bytes_decompressed = actual_out_bytes;
        if (comp_buf_size > actual_out_bytes)
            res = EXR_ERR_CORRUPT_CHUNK;
        else
            internal_zip_reconstruct_bytes (
                uncompressed_data, scratch_data, actual_out_bytes);
    }

    return res;
}
```

The `uncompressed_size` comes from the `unpacked_size` extracted earlier, and the `uncompressed_data` is a buffer allocated by making space for the size "advertised" in the chunk information.

However, `scratch_data` and `actual_out_bytes` will contain, after decompression, the uncompressed data and its size, respectively. 

The vulnerability lies in the fact that the `undo_zip_impl` function lacks code to check whether `actual_out_bytes` is greater than `uncompressed_size`. 

The effect is that, by setting the `unpacked_size` in the chunk header smaller than the actual chunk decompressed data, it is possible - in the `internal_zip_reconstruct_bytes` function - to overflow past the boundaries of a heap chunk.

### PoC

NOTE: you can download the `heap_overflow.exr` file from this link:

https://github.com/ShielderSec/poc/tree/main/CVE-2025-48071

1. Compile the `exrcheck` binary in a macOS or GNU/Linux machine with ASAN.
2. Open the `heap_overflow.exr` file with the following command:

```
exrcheck heap_overflow.exr
```

3. Notice that `exrcheck` crashes with an ASAN stack-trace.
![image](https://github.com/user-attachments/assets/57907073-bc9f-40bb-9030-16008035ade8)

### Impact

An attacker might exploit this vulnerability by feeding a maliciously crafted file to a program that uses the OpenEXR libraries, thus gaining the capability to write an arbitrary amount of bytes in the heap. This could potentially result in code execution in the process.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-h45x-qhg2-q375
- https://nvd.nist.gov/vuln/detail/CVE-2025-48071
- https://github.com/AcademySoftwareFoundation/openexr/commit/916cc729e24aa16b86d82813f6e136340ab2876f
- https://github.com/AcademySoftwareFoundation/openexr
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.3
- https://github.com/ShielderSec/poc/tree/main/CVE-2025-48071
