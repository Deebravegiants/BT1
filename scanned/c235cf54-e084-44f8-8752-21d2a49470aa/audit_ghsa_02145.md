# [M] Reference binding to nullptr in `MatrixDiagV*` ops

## Summary
Severity: Medium
Advisory: GHSA-5xwc-mrhx-5g3m
CVE: CVE-2021-37657
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-5xwc-mrhx-5g3m
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
An attacker can cause undefined behavior via binding a reference to null pointer in all operations of type `tf.raw_ops.MatrixDiagV*`:

```python
import tensorflow as tf

tf.raw_ops.MatrixDiagV3(
  diagonal=[1,0],
  k=[],
  num_rows=[1,2,3],
  num_cols=[4,5],
  padding_value=[],
  align='RIGHT_RIGHT')
``` 

The [implementation](https://github.com/tensorflow/tensorflow/blob/84d053187cb80d975ef2b9684d4b61981bca0c41/tensorflow/core/kernels/linalg/matrix_diag_op.cc) has incomplete validation that the value of `k` is a valid tensor. We have check that this value is either a scalar or a vector, but there is no check for the number of elements. If this is an empty tensor, then code that accesses the first element of the tensor is wrong:

```cc
  auto& diag_index = context->input(1);
  ...
  lower_diag_index = diag_index.flat<int32>()(0);
```

### Patches
We have patched the issue in GitHub commit [f2a673bd34f0d64b8e40a551ac78989d16daad09](https://github.com/tensorflow/tensorflow/commit/f2a673bd34f0d64b8e40a551ac78989d16daad09).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5xwc-mrhx-5g3m
- https://nvd.nist.gov/vuln/detail/CVE-2021-37657
- https://github.com/tensorflow/tensorflow/commit/f2a673bd34f0d64b8e40a551ac78989d16daad09
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-570.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-768.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-279.yaml
- https://github.com/tensorflow/tensorflow
