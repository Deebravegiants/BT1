# [M] Segfault due to negative splits in `SplitV`

## Summary
Severity: Medium
Advisory: GHSA-cpf4-wx82-gxp6
CVE: CVE-2021-41222
CWE: CWE-682
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-cpf4-wx82-gxp6
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
The [implementation](https://github.com/tensorflow/tensorflow/blob/e71b86d47f8bc1816bf54d7bddc4170e47670b97/tensorflow/core/kernels/split_v_op.cc#L49-L205) of `SplitV` can trigger a segfault is an attacker supplies negative arguments:

```python
import tensorflow as tf

tf.raw_ops.SplitV(
  value=tf.constant([]),
  size_splits=[-1, -2]
  ,axis=0,
  num_split=2)
``` 
  
This occurs whenever `size_splits` contains more than one value and at least one value is negative.
  
### Patches 
We have patched the issue in GitHub commit [25d622ffc432acc736b14ca3904177579e733cc6](https://github.com/tensorflow/tensorflow/commit/25d622ffc432acc736b14ca3904177579e733cc6).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cpf4-wx82-gxp6
- https://nvd.nist.gov/vuln/detail/CVE-2021-41222
- https://github.com/tensorflow/tensorflow/commit/25d622ffc432acc736b14ca3904177579e733cc6
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-631.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-829.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-414.yaml
- https://github.com/tensorflow/tensorflow
