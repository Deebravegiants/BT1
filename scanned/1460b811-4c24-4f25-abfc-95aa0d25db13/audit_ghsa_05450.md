# [M] vLLM is vulnerable to DoS in Idefics3 vision models via image payload with ambiguous dimensions

## Summary
Severity: Medium
Advisory: GHSA-grg2-63fw-f2qr
CVE: CVE-2026-22773
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-grg2-63fw-f2qr
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.6.4 <0.12.0

## Details
### Summary
Users can crash the vLLM engine serving multimodal models that use the _Idefics3_ vision model implementation by sending a specially crafted 1x1 pixel image. This causes a tensor dimension mismatch that results in an unhandled runtime error, leading to complete server termination.

### Details
The vulnerability is triggered when the image processor encounters a 1x1 pixel image with shape (1, 1, 3) in HWC (Height, Width, Channel) format. Due to the ambiguous dimensions, the processor incorrectly assumes the image is in CHW (Channel, Height, Width) format with shape (3, H, W). This misinterpretation causes an incorrect calculation of the number of image patches, resulting in a fatal tensor split operation failure.

**Crash location**: `vllm/model_executor/models/idefics3.py` line 672:
```python
def _process_image_input(self, image_input: ImageInputs) -> torch.Tensor | list[torch.Tensor]:
    # ...
    num_patches = image_input["num_patches"]
    return [e.flatten(0, 1) for e in image_features.split(num_patches.tolist())]
```

The `split()` call fails because the computed `num_patches` value (17) does not match the actual tensor dimension (9):
```
RuntimeError: split_with_sizes expects split_sizes to sum exactly to 9 
(input tensor's size at dimension 0), but got split_sizes=[17]
```

This unhandled exception terminates the EngineCore process, crashing the server.

#### Affected Models
Any model using the Idefics3 architecture. The vulnerability was tested with `HuggingFaceTB/SmolVLM-Instruct`.

### Impact
Denial of service by crashing the engine

### Mitigation
Validating the input:
```python
def _validate_image_dimensions(self, image_shape):
    h, w = image_shape[:2] if len(image_shape) == 3 else image_shape
    if h < MIN_IMAGE_SIZE or w < MIN_IMAGE_SIZE:
        raise ValueError(f"Image dimensions too small: {h}x{w}")
```

Managing the exception:
```python
try:
    return [e.flatten(0, 1) for e in image_features.split(num_patches.tolist())]
except RuntimeError as e:
    logger.error(f"Image processing failed: {e}")
    raise InvalidImageError("Failed to process image features") from e
```

### Fixes

* https://github.com/vllm-project/vllm/pull/29881

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-grg2-63fw-f2qr
- https://nvd.nist.gov/vuln/detail/CVE-2026-22773
- https://github.com/vllm-project/vllm/pull/29881
- https://github.com/vllm-project/vllm/commit/0ec84221718d920c3f46da879cc354f94b8fb59e
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-143.yaml
- https://github.com/vllm-project/vllm
