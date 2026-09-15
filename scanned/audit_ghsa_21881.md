# [H] Segfault in `simplifyBroadcast` in Tensorflow

## Summary
Severity: High
Advisory: GHSA-gwcx-jrx4-92w2
CVE: CVE-2022-23593
CWE: CWE-754
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-gwcx-jrx4-92w2
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.8.0-rc0 <2.8.0
- PyPI: `tensorflow-cpu` — affected >=2.8.0-rc0 <2.8.0
- PyPI: `tensorflow-gpu` — affected >=2.8.0-rc0 <2.8.0

## Details
### Impact
The [`simplifyBroadcast` function in the MLIR-TFRT infrastructure in TensorFlow](https://github.com/tensorflow/tensorflow/blob/274df9b02330b790aa8de1cee164b70f72b9b244/tensorflow/compiler/mlir/tfrt/jit/transforms/tf_cpurt_symbolic_shape_optimization.cc#L149-L205) is vulnerable to a segfault (hence, denial of service), if called with scalar shapes.

```cc 
  size_t maxRank = 0;
  for (auto shape : llvm::enumerate(shapes)) {
    auto found_shape = analysis.dimensionsForShapeTensor(shape.value());
    if (!found_shape) return {};
    shapes_found.push_back(*found_shape);
    maxRank = std::max(maxRank, found_shape->size());
  }   

  SmallVector<const ShapeComponentAnalysis::SymbolicDimension*>
      joined_dimensions(maxRank);
```

If all shapes are scalar, then `maxRank` is 0, so we build an empty `SmallVector`.

### Patches
We have patched the issue in GitHub commit [35f0fabb4c178253a964d7aabdbb15c6a398b69a](https://github.com/tensorflow/tensorflow/commit/35f0fabb4c178253a964d7aabdbb15c6a398b69a).

The fix will be included in TensorFlow 2.8.0. This is the only affected version.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gwcx-jrx4-92w2
- https://nvd.nist.gov/vuln/detail/CVE-2022-23593
- https://github.com/tensorflow/tensorflow/commit/35f0fabb4c178253a964d7aabdbb15c6a398b69a
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-102.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-157.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/274df9b02330b790aa8de1cee164b70f72b9b244/tensorflow/compiler/mlir/tfrt/jit/transforms/tf_cpurt_symbolic_shape_optimization.cc#L149-L205
