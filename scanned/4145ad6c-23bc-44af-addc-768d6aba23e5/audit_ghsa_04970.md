# [M] vLLM: GGUF dequantize kernel int truncation exposes uninitialized GPU memory in multi-tenant serving

## Summary
Severity: Medium
Advisory: GHSA-5jv2-g5wq-cmr4
CVE: CVE-2026-53923
CWE: CWE-200, CWE-681
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-5jv2-g5wq-cmr4
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.5.5 <0.24.0

## Details
## Summary

Integer truncation of tensor dimensions in vLLM's GGUF dequantize kernels (`csrc/quantization/gguf/gguf_kernel.cu`) causes partial tensor processing. The output tensor is allocated at full size via `torch::empty` (uninitialized memory), but the dequantize CUDA kernel processes only a truncated number of elements. The unfilled portion of the output tensor retains whatever was previously in GPU memory. In multi-tenant inference deployments, this residual GPU memory may contain tensor data from other users' inference requests, constituting information disclosure.

## Root Cause

The `to_cuda_ggml_t` function pointer type at `ggml-common.h:1067` declares its element count parameter as `int` (32-bit):

```cpp
using to_cuda_ggml_t = void (*)(const void * __restrict__ x,
                                dst_t * __restrict__ y,
                                int k,              // 32-bit
                                cudaStream_t stream);
```

All dequantize kernel functions (`dequantize_block_cuda`, `dequantize_row_q2_K_cuda`, etc. in `dequantize.cuh`) inherit this `int k` parameter and use it as the kernel launch grid size:

```cpp
static void dequantize_block_cuda(..., const int k, cudaStream_t stream) {
    const int num_blocks = (k + 2*CUDA_DEQUANTIZE_BLOCK_SIZE - 1) / (2*CUDA_DEQUANTIZE_BLOCK_SIZE);
    dequantize_block<<<num_blocks, CUDA_DEQUANTIZE_BLOCK_SIZE, 0, stream>>>(vx, y, k);
}
```

In `ggml_dequantize()` at `gguf_kernel.cu:85`, the caller passes `m * n` (an `int64_t` product) to this `int k` parameter:

```cpp
at::Tensor DW = torch::empty({m, n}, options);    // line 80: full-size, UNINITIALIZED
// ...
to_cuda((void*)W.data_ptr(), (scalar_t*)DW.data_ptr(), m * n, stream);  // line 85: m*n truncated to int
```

When `m * n > INT_MAX`, the truncated `k` is smaller than the actual tensor size. The kernel processes `k` elements. The remaining `(m * n) - k` elements in `DW` are never written and contain stale GPU memory.

This is a single root cause -- the `int` type on the `k` parameter in `to_cuda_ggml_t` -- with a single fix: change `int k` to `int64_t k`. All dequantize functions inherit this type through the same typedef.

## Affected Functions

All in `csrc/quantization/gguf/gguf_kernel.cu`:

| Function | Line | Allocation | Info Disclosure? |
|----------|------|-----------|-----------------|
| `ggml_dequantize` | 74 | `torch::empty({m, n})` at line 80 | Yes -- `m*n` truncated to `int k` at line 85 |
| `ggml_mul_mat_vec_a8` | 91 | `torch::empty({vecs, row})` at line 99 | Yes -- `int col = X.sizes()[1]` at line 94 |
| `ggml_mul_mat_a8` | 207 | `torch::empty({batch, row})` at line 215 | Yes -- `int col = X.sizes()[1]` at line 210 |
| `ggml_moe_a8` | 279 | `torch::empty({tokens*top_k, row})` at line 289 | Yes -- `int col = X.sizes()[1]` at line 285 |

All four functions allocate output tensors with `torch::empty` (uninitialized) and then run CUDA kernels that use truncated dimension values as loop bounds. The unfilled portion of each output tensor retains stale GPU memory.

`ggml_moe_a8_vec` (line 382) uses `torch::zeros` instead of `torch::empty`, so it is not affected by the info disclosure variant.

## Impact: Information Disclosure in Multi-Tenant Serving

vLLM is designed for multi-tenant inference serving. GPU memory is reused across requests from different users. When the dequantize kernel partially fills an output tensor:

1. The output tensor `DW` is allocated with `torch::empty` -- the buffer contains whatever was previously in that GPU memory region
2. The dequantize kernel fills only a truncated portion of the buffer
3. The unfilled portion retains residual data from prior GPU operations, which may include tensor data from other users' inference requests
4. The contaminated tensor proceeds through the model computation
5. No error or warning is generated -- the partial fill is silent

This is a confidentiality violation. In shared inference deployments (the primary vLLM use case), one user's inference data can leak into another user's model computation through residual GPU memory.

## Attacker Control

The attacker crafts a GGUF model file with weight tensor dimensions whose product exceeds `INT_MAX` (e.g., a matrix with shape `[65536, 65536]` gives `m * n = 4,294,967,296`). The model is hosted on HuggingFace or any model hub. The victim loads the model with vLLM for inference serving. The truncation happens automatically during model weight dequantization.

## Fix

A fix for this vulnerability was added here: https://github.com/vllm-project/vllm/pull/44971

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-5jv2-g5wq-cmr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-53923
- https://github.com/vllm-project/vllm/pull/44971
- https://github.com/vllm-project/vllm/commit/f219788f91952827132fa4fdf916427cd20d225e
- https://github.com/advisories/GHSA-5jv2-g5wq-cmr4
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-3403.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
