# [M] vLLM has a Weakness in MultiModalHasher Image Hashing Implementation

## Summary
Severity: Medium
Advisory: GHSA-c65p-x677-fgj6
CVE: CVE-2025-46722
CWE: CWE-1023, CWE-1288
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-c65p-x677-fgj6
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.7.0 <0.9.0

## Details
## Summary

In the file `vllm/multimodal/hasher.py`, the `MultiModalHasher` class has a security and data integrity issue in its image hashing method. Currently, it serializes `PIL.Image.Image` objects using only `obj.tobytes()`, which returns only the raw pixel data, without including metadata such as the image’s shape (width, height, mode). As a result, two images of different sizes (e.g., 30x100 and 100x30) with the same pixel byte sequence could generate the same hash value. This may lead to hash collisions, incorrect cache hits, and even data leakage or security risks.

## Details

- **Affected file:** `vllm/multimodal/hasher.py`
- **Affected method:** `MultiModalHasher.serialize_item`
https://github.com/vllm-project/vllm/blob/9420a1fc30af1a632bbc2c66eb8668f3af41f026/vllm/multimodal/hasher.py#L34-L35
- **Current behavior:** For `Image.Image` instances, only `obj.tobytes()` is used for hashing.
- **Problem description:** `obj.tobytes()` does not include the image’s width, height, or mode metadata.
- **Impact:** Two images with the same pixel byte sequence but different sizes could be regarded as the same image by the cache and hashing system, which may result in:
    - Incorrect cache hits, leading to abnormal responses
    - Deliberate construction of images with different meanings but the same hash value


## Recommendation

In the `serialize_item` method, **serialization of `Image.Image` objects should include not only pixel data, but also all critical metadata**—such as dimensions (`size`), color mode (`mode`), format, and especially the `info` dictionary. The `info` dictionary is particularly important in palette-based images (e.g., mode `'P'`), where the palette itself is stored in `info`. Ignoring `info` can result in hash collisions between visually distinct images with the same pixel bytes but different palettes or metadata. This can lead to incorrect cache hits or even data leakage.

**Summary:**  
Serializing only the raw pixel data is insecure. Always include all image metadata (`size`, `mode`, `format`, `info`) in the hash calculation to prevent collisions, especially in cases like palette-based images.

**Impact for other modalities**
For the influence of other modalities, since the video modality is transformed into a multi-dimensional array containing the length, width, time, etc. of the video, the same problem exists due to the incorrect sequence of numpy as well.

For audio, since the momo function is not enabled in librosa.load, the loaded audio is automatically encoded into single channels by librosa and returns a one-dimensional array of numpy, thus keeping the structure of numpy fixed and not affected by this issue.

## Fixes

* https://github.com/vllm-project/vllm/pull/17378

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-c65p-x677-fgj6
- https://nvd.nist.gov/vuln/detail/CVE-2025-46722
- https://github.com/vllm-project/vllm/pull/17378
- https://github.com/vllm-project/vllm/commit/99404f53c72965b41558aceb1bc2380875f5d848
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2025-43.yaml
- https://github.com/vllm-project/vllm
