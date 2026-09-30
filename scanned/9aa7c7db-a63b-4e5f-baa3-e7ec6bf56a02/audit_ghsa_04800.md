# [M] vLLM: image EXIF Rotation & PNG tRNS Transparency Not Normalized, Causing Mismatch Between Model Input and Expectations

## Summary
Severity: Medium
Advisory: GHSA-8jr5-v98p-w75m
CVE: CVE-2026-12491
CWE: CWE-436
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-8jr5-v98p-w75m
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.11.0 <0.24.0

## Details
## Summary

Issue 1: EXIF orientation not normalized → The image orientation processed by the model differs from how humans view it, introducing interpretation bias.

Issue 2: PNG tRNS not explicitly flattened before converting to RGB → After conversion, transparent/semi-transparent pixels are rendered unexpectedly, making otherwise subtle overlay elements visible and distorting the input content. (This attack is similar to AlphaDog: RGBA handling is already correct in vLLM, but since tRNS permits RGB images, the correct processing path isn’t taken.)

Issue 3 : Pillow only loads the first frame when loading APNG or GIF files.

---

## Root Cause

* **Rotation**: After opening an image, `ImageOps.exif_transpose` is not called to normalize EXIF orientation.
* **Transparency**: Only **RGBA→RGB** is flattened with a background; PNGs carrying **`tRNS`** in **`P`/`L`/`RGB + tRNS`** and other non-RGBA modes take the `image.convert("RGB")` path, which implicitly discards/remaps transparency semantics.

---

## Affected Code


https://github.com/vllm-project/vllm/blob/16b37f3119918c1e5a39f303e0d0892c65c07a90/vllm/multimodal/image.py#L77-L84

https://github.com/vllm-project/vllm/blob/16b37f3119918c1e5a39f303e0d0892c65c07a90/vllm/multimodal/image.py#L37-L43

https://github.com/vllm-project/vllm/blob/16b37f3119918c1e5a39f303e0d0892c65c07a90/vllm/multimodal/image.py#L26-L34
> Current state: `ImageOps.exif_transpose` is not used. (Although the `rescale_image_size` function ([https://github.com/vllm-project/vllm/blob/main/vllm/multimodal/image.py#L14](https://github.com/vllm-project/vllm/blob/main/vllm/multimodal/image.py#L14)) exists and includes a `transpose` parameter, I’ve found that it doesn’t seem to be called anywhere outside the `test` directory.）

> **Call order**: `_convert_image_mode` runs first; if the conditions are met, `convert_image_mode` is called.
> 
> **Issue**: Only the “RGBA → RGB” path is explicitly flattened. `P`, `L`, or `RGB` with `tRNS` all fall back to `image.convert("RGB")`. For PNGs that include `tRNS`, `convert("RGB")` directly produces 24-bit RGB, leading to:
> 
> * **`P` mode**: The transparent index becomes an actual RGB color (often black, white, or an undefined background), so transparency is lost.
> * **`L/LA` and `RGB + tRNS`**: `convert("RGB")` doesn’t composite against a chosen background first, so elements that relied on transparency to be hidden or softened become solid.


## Impact & Scope

* **Impact**: Pixels the model sees can diverge from operator expectations (due to orientation or transparency handling), potentially altering downstream reasoning.
* **Scope**: The image I/O and mode-conversion paths in `vllm/multimodal/image.py`. The existing **RGBA→RGB** flattening is correct; the issues center on **missing EXIF normalization** and **non-RGBA `tRNS` not being explicitly composited**.

## Case
EXIF： http://qiniu.funxingzuo.top/exif_orient_180.jpg
tRNS:  http://qiniu.funxingzuo.top/hello.png

## Fix

A fix for this vulnerability was merged here: https://github.com/vllm-project/vllm/pull/44974

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-8jr5-v98p-w75m
- https://nvd.nist.gov/vuln/detail/CVE-2026-12491
- https://github.com/vllm-project/vllm/pull/44974
- https://github.com/vllm-project/vllm/commit/cf1c90672404548aa3bc51f92c4745576a65ee26
- https://access.redhat.com/security/cve/CVE-2026-12491
- https://bugzilla.redhat.com/show_bug.cgi?id=2489786
- https://github.com/advisories/GHSA-8jr5-v98p-w75m
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-3406.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
