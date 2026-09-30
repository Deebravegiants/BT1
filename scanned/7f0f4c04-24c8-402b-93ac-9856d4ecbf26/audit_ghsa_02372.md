# [M] Reference binding to nullptr in `MatrixSetDiagV*` ops

## Summary
Severity: Medium
Advisory: GHSA-6p5r-g9mq-ggh2
CVE: CVE-2021-37658
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-6p5r-g9mq-ggh2
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
An attacker can cause undefined behavior via binding a reference to null pointer in all operations of type `tf.raw_ops.MatrixSetDiagV*`:

```python
import tensorflow as tf

tf.raw_ops.MatrixSetDiagV3(
  input=[1,2,3],
  diagonal=[1,1],
  k=[],
  align='RIGHT_LEFT')
```
  
The  [implementation](https://github.com/tensorflow/tensorflow/blob/84d053187cb80d975ef2b9684d4b61981bca0c41/tensorflow/core/kernels/linalg/matrix_diag_op.cc) has incomplete validation that the value of `k` is a valid tensor. We have check that this value is either a scalar or a vector, but there is no check for the number of elements. If this is an empty tensor, then code that accesses the first element of the tensor is wrong: 

```cc 
  auto& diag_index = context->input(1);
  ...
  lower_diag_index = diag_index.flat<int32>()(0);
```
  
### Patches
We have patched the issue in GitHub commit [ff8894044dfae5568ecbf2ed514c1a37dc394f1b](https://github.com/tensorflow/tensorflow/commit/ff8894044dfae5568ecbf2ed514c1a37dc394f1b).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-6p5r-g9mq-ggh2
- https://nvd.nist.gov/vuln/detail/CVE-2021-37658
- https://github.com/tensorflow/tensorflow/commit/ff8894044dfae5568ecbf2ed514c1a37dc394f1b
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-571.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-769.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-280.yaml
- https://github.com/tensorflow/tensorflow
