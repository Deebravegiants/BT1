# [M] TensorFlow vulnerable to `CHECK` failure in `TensorListReserve` via missing validation

## Summary
Severity: Medium
Advisory: GHSA-v5xg-3q2c-c2r4
CVE: CVE-2022-35960
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-v5xg-3q2c-c2r4
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1

## Details
### Impact
In [`core/kernels/list_kernels.cc's TensorListReserve`](https://github.com/tensorflow/tensorflow/blob/c8ba76d48567aed347508e0552a257641931024d/tensorflow/core/kernels/list_kernels.cc#L322-L325), `num_elements` is assumed to be a tensor of size 1. When a `num_elements` of more than 1 element is provided, then `tf.raw_ops.TensorListReserve` fails the `CHECK_EQ` in `CheckIsAlignedAndSingleElement`.
```python
import tensorflow as tf

tf.raw_ops.TensorListReserve(element_shape=(1,1), num_elements=tf.constant([1,1], dtype=tf.int32), element_dtype=tf.int8)
```

### Patches
We have patched the issue in GitHub commit [b5f6fbfba76576202b72119897561e3bd4f179c7](https://github.com/tensorflow/tensorflow/commit/b5f6fbfba76576202b72119897561e3bd4f179c7).


The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Kang Hong Jin from Singapore Management University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-v5xg-3q2c-c2r4
- https://nvd.nist.gov/vuln/detail/CVE-2022-35960
- https://github.com/tensorflow/tensorflow/commit/b5f6fbfba76576202b72119897561e3bd4f179c7
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/c8ba76d48567aed347508e0552a257641931024d/tensorflow/core/kernels/list_kernels.cc#L322-L325
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
