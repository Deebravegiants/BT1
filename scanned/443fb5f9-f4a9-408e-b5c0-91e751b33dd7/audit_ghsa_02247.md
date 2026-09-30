# [H] Reference binding to nullptr in unicode encoding

## Summary
Severity: High
Advisory: GHSA-w74j-v8xh-3w5h
CVE: CVE-2021-37667
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-w74j-v8xh-3w5h
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.3.4
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
An attacker can cause undefined behavior via binding a reference to null pointer in `tf.raw_ops.UnicodeEncode`:

```python
import tensorflow as tf
from tensorflow.python.ops import gen_string_ops

gen_string_ops.unicode_encode(
  input_values=[],
  input_splits=[],
  output_encoding='UTF-8',
  errors='ignore',
  replacement_char='a')
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/unicode_ops.cc#L533-L539) reads the first dimension of the `input_splits` tensor before validating that this tensor is not empty: 

```cc
  const Tensor& input_splits = context->input(1);
  const auto input_splits_flat = input_splits.flat<SPLITS_TYPE>();
  TensorShape output_shape({input_splits.dim_size(0) - 1});
```

### Patches
We have patched the issue in GitHub commit [2e0ee46f1a47675152d3d865797a18358881d7a6](https://github.com/tensorflow/tensorflow/commit/2e0ee46f1a47675152d3d865797a18358881d7a6).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-w74j-v8xh-3w5h
- https://nvd.nist.gov/vuln/detail/CVE-2021-37667
- https://github.com/tensorflow/tensorflow/commit/2e0ee46f1a47675152d3d865797a18358881d7a6
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-580.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-778.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-289.yaml
- https://github.com/tensorflow/tensorflow
