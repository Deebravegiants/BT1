# [M] Integer overflow due to conversion to unsigned

## Summary
Severity: Medium
Advisory: GHSA-9w2p-5mgw-p94c
CVE: CVE-2021-37645
CWE: CWE-681
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9w2p-5mgw-p94c
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
The implementation of `tf.raw_ops.QuantizeAndDequantizeV4Grad` is vulnerable to an integer overflow issue caused by converting a signed integer value to an unsigned one and then allocating memory based on this value.

```python
import tensorflow as tf

tf.raw_ops.QuantizeAndDequantizeV4Grad(
  gradients=[1.0,2.0],
  input=[1.0,1.0],
  input_min=[0.0],
  input_max=[10.0],
  axis=-100)
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/quantize_and_dequantize_op.cc#L126) uses the `axis` value as the size argument to `absl::InlinedVector` constructor. But, the constructor uses an unsigned type for the argument, so the implicit conversion transforms the negative value to a large integer.

### Patches
We have patched the issue in GitHub commit [96f364a1ca3009f98980021c4b32be5fdcca33a1](https://github.com/tensorflow/tensorflow/commit/96f364a1ca3009f98980021c4b32be5fdcca33a1).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, and TensorFlow 2.4.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9w2p-5mgw-p94c
- https://nvd.nist.gov/vuln/detail/CVE-2021-37645
- https://github.com/tensorflow/tensorflow/commit/96f364a1ca3009f98980021c4b32be5fdcca33a1
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-558.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-756.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-267.yaml
- https://github.com/tensorflow/tensorflow
