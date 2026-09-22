# [H] Null pointer dereference in `RaggedTensorToTensor`

## Summary
Severity: High
Advisory: GHSA-hwr7-8gxx-fj5p
CVE: CVE-2021-37638
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hwr7-8gxx-fj5p
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
Sending invalid argument for `row_partition_types` of `tf.raw_ops.RaggedTensorToTensor` API results in a null pointer dereference and undefined behavior:

```python
import tensorflow as tf

tf.raw_ops.RaggedTensorToTensor(
  shape=1,
  values=10,
  default_value=21,
  row_partition_tensors=tf.constant([0,0,0,0]),
  row_partition_types=[])
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/47a06f40411a69c99f381495f490536972152ac0/tensorflow/core/kernels/ragged_tensor_to_tensor_op.cc#L328) accesses the first element of a user supplied list of values without validating that the provided list is not empty.

### Patches
We have patched the issue in GitHub commit [301ae88b331d37a2a16159b65b255f4f9eb39314](https://github.com/tensorflow/tensorflow/commit/301ae88b331d37a2a16159b65b255f4f9eb39314).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hwr7-8gxx-fj5p
- https://nvd.nist.gov/vuln/detail/CVE-2021-37638
- https://github.com/tensorflow/tensorflow/commit/301ae88b331d37a2a16159b65b255f4f9eb39314
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-551.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-749.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-260.yaml
- https://github.com/tensorflow/tensorflow
