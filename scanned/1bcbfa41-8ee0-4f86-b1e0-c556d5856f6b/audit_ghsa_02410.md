# [H] Reference binding to nullptr and heap OOB in binary cwise ops

## Summary
Severity: High
Advisory: GHSA-q3g3-h9r4-prrc
CVE: CVE-2021-37659
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-q3g3-h9r4-prrc
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
An attacker can cause undefined behavior via binding a reference to null pointer in all binary cwise operations that don't require broadcasting (e.g., gradients of binary cwise operations):

```python
import tensorflow as tf

tf.raw_ops.SqrtGrad(y=[4, 16],dy=[])
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/84d053187cb80d975ef2b9684d4b61981bca0c41/tensorflow/core/kernels/cwise_ops_common.h#L264) assumes that the two inputs have exactly the same number of elements but does not check that. Hence, when the eigen functor executes it triggers heap OOB reads and undefined behavior due to binding to nullptr.

### Patches
We have patched the issue in GitHub commit [93f428fd1768df147171ed674fee1fc5ab8309ec](https://github.com/tensorflow/tensorflow/commit/93f428fd1768df147171ed674fee1fc5ab8309ec).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution 
This vulnerability has been reported by members of the Aivul Team from Qihoo  360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-q3g3-h9r4-prrc
- https://nvd.nist.gov/vuln/detail/CVE-2021-37659
- https://github.com/tensorflow/tensorflow/commit/93f428fd1768df147171ed674fee1fc5ab8309ec
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-572.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-770.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-281.yaml
- https://github.com/tensorflow/tensorflow
