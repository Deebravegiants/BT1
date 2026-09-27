# [H] Null pointer dereference in `MatrixDiagPartOp`

## Summary
Severity: High
Advisory: GHSA-fcwc-p4fc-c5cc
CVE: CVE-2021-37643
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-fcwc-p4fc-c5cc
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
If a user does not provide a valid padding value to `tf.raw_ops.MatrixDiagPartOp`, then the code triggers a null pointer dereference (if input is empty) or produces invalid behavior, ignoring all values after the first:

```python
import tensorflow as tf

tf.raw_ops.MatrixDiagPartV2(
  input=tf.ones(2,dtype=tf.int32),
  k=tf.ones(2,dtype=tf.int32),
  padding_value=[])
```

Although this example is given for `MatrixDiagPartV2`, all versions of the operation are affected.

The [implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/linalg/matrix_diag_op.cc#L89) reads the first value from a tensor buffer without first checking that the tensor has values to read from.

### Patches
We have patched the issue in GitHub commit [482da92095c4d48f8784b1f00dda4f81c28d2988](https://github.com/tensorflow/tensorflow/commit/482da92095c4d48f8784b1f00dda4f81c28d2988).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-fcwc-p4fc-c5cc
- https://nvd.nist.gov/vuln/detail/CVE-2021-37643
- https://github.com/tensorflow/tensorflow/commit/482da92095c4d48f8784b1f00dda4f81c28d2988
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-556.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-754.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-265.yaml
- https://github.com/tensorflow/tensorflow
