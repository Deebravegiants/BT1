# [M] ONNX has Null Pointer Dereference in Upsample Version Converter Adapter (Zero Inputs)

## Summary
Severity: Medium
Advisory: GHSA-hwpq-hmq9-wj77
CVE: CVE-2026-44512
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-hwpq-hmq9-wj77
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=1.9.0 <1.22.0

## Details
### Summary

Null pointer dereference (SIGSEGV) in `Upsample_6_7::adapt_upsample_6_7()` (`onnx/version_converter/adapters/upsample_6_7.h:31`) when `convert_version()` processes a model with an Upsample node that has zero inputs. The adapter accesses `node->inputs()[0]->sizes()` without checking input count. 107-byte PoC crashes on Release build.

This is the same class of bug as the Cast adapter advisory (separate report) but in a different adapter, different file, and different operator.

### Details

The Upsample 6→7 adapter validates attributes but not inputs:
```cpp
// upsample_6_7.h:20-33
void adapt_upsample_6_7(..., Node* node) const {
    ONNX_ASSERTM(
        node->hasAttribute(width_scale_symbol) && node->hasAttribute(height_scale_symbol),
        "...")  // Attribute check PASSES

    auto width_scale = node->f(width_scale_symbol);
    auto height_scale = node->f(height_scale_symbol);

    auto input_shape = node->inputs()[0]->sizes();
    //                 ^^^^^^^^^^^^^^^^^^^^
    //                 OOB when inputs().size() == 0 → SIGSEGV
}
```

The PoC has an Upsample node at opset 6 with the required `width_scale` and `height_scale` attributes but zero inputs. The attribute assertions pass, then `node->inputs()[0]` on an empty `ArrayRef`:
- Release builds (`NDEBUG`): bounds-check assertion compiled out → reads garbage pointer → SIGSEGV
- Debug builds: `assert(Index < Length)` at `array_ref.h:159` → SIGABRT

An Upsample node with zero inputs passes `graphProtoToGraph()` because the import code only resolves input names present in the protobuf.

### PoC
```python
import base64
import onnx
from onnx import version_converter

poc_b64 = "CAI6YQo8EgFZIghVcHNhbXBsZSoVCgt3aWR0aF9zY2FsZRUAAABAoAEBKhYKDGhlaWdodF9zY2FsZRUAAABAoAEBEgR0ZXN0YhsKAVkSFgoUCAESEAoCCAEKAggBCgIIBAoCCARCBAoAEAY="

model = onnx.load_from_string(base64.b64decode(poc_b64))

# CRASHES — Upsample_6_7 adapter dereferences empty inputs array
version_converter.convert_version(model, 7)  # SIGSEGV
```

107-byte PoC. Confirmed SIGSEGV on both onnx 1.21.0 (pip) and 1.22.0 (source build).

### Impact

Any application that uses `onnx.version_converter.convert_version()` on untrusted models is vulnerable. This includes model conversion pipelines and tools that auto-upgrade opset versions for compatibility. The crash is unrecoverable (SIGSEGV). 

This vulnerability is part of a systemic pattern across multiple version converter adapters. A full audit of all ~45 adapters was performed as part of the fix; eight adapters were found with the same class of unguarded indexed access (cast_9_8, softmax_12_13, softmax_13_12, upsample_6_7, upsample_9_10, group_normalization_20_21, broadcast_forward_compatibility, upsample_9_8) and all have been fixed in PR #7813.

## References
- https://github.com/onnx/onnx/security/advisories/GHSA-hwpq-hmq9-wj77
- https://github.com/onnx/onnx/pull/7916
- https://github.com/onnx/onnx
- https://github.com/onnx/onnx/releases/tag/v1.22.0
