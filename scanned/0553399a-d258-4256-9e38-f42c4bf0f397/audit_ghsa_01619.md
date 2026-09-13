# [H] Segfault in `tf.quantization.quantize_and_dequantize`

## Summary
Severity: High
Advisory: GHSA-rrfp-j2mp-hq9c
CVE: CVE-2020-15265
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-11-13
Source: https://github.com/advisories/GHSA-rrfp-j2mp-hq9c
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.4.0
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.0
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.0

## Details
### Impact
An attacker can pass an invalid `axis` value to `tf.quantization.quantize_and_dequantize`:

```python
tf.quantization.quantize_and_dequantize(
    input=[2.5, 2.5], input_min=[0,0], input_max=[1,1], axis=10)
```

This results in accessing [a dimension outside the rank of the input tensor](https://github.com/tensorflow/tensorflow/blob/0225022b725993bfc19b87a02a2faaad9a53bc17/tensorflow/core/kernels/quantize_and_dequantize_op.cc#L74) in the C++ kernel implementation:
```
const int depth = (axis_ == -1) ? 1 : input.dim_size(axis_);
```

However, [`dim_size` only does a `DCHECK`](https://github.com/tensorflow/tensorflow/blob/0225022b725993bfc19b87a02a2faaad9a53bc17/tensorflow/core/framework/tensor_shape.cc#L292-L307) to validate the argument and then uses it to access the corresponding element of an array:
```
int64 TensorShapeBase<Shape>::dim_size(int d) const {
  DCHECK_GE(d, 0);
  DCHECK_LT(d, dims());
  DoStuffWith(dims_[d]);
}
```

Since in normal builds, `DCHECK`-like macros are no-ops, this results in segfault and access out of bounds of the array.

### Patches

We have patched the issue in eccb7ec454e6617738554a255d77f08e60ee0808 and will release TensorFlow 2.4.0 containing the patch. TensorFlow nightly packages after this commit will also have the issue resolved.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported in #42105

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rrfp-j2mp-hq9c
- https://nvd.nist.gov/vuln/detail/CVE-2020-15265
- https://github.com/tensorflow/tensorflow/issues/42105
- https://github.com/tensorflow/tensorflow/commit/eccb7ec454e6617738554a255d77f08e60ee0808
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-295.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-330.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-138.yaml
- https://github.com/tensorflow/tensorflow
