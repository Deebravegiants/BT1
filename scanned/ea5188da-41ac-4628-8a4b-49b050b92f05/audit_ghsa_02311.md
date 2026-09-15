# [H] Reference binding to nullptr in `RaggedTensorToVariant`

## Summary
Severity: High
Advisory: GHSA-w4xf-2pqw-5mq7
CVE: CVE-2021-37666
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-w4xf-2pqw-5mq7
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
An attacker can cause undefined behavior via binding a reference to null pointer in `tf.raw_ops.RaggedTensorToVariant`:

```python
import tensorflow as tf

tf.raw_ops.RaggedTensorToVariant(
  rt_nested_splits=[],
  rt_dense_values=[1,2,3],
  batched_input=True)
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/ragged_tensor_to_variant_op.cc#L129) has an incomplete validation of the splits values, missing the case when the argument would be empty.

### Patches
We have patched the issue in GitHub commit [be7a4de6adfbd303ce08be4332554dff70362612](https://github.com/tensorflow/tensorflow/commit/be7a4de6adfbd303ce08be4332554dff70362612).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
  
### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-w4xf-2pqw-5mq7
- https://nvd.nist.gov/vuln/detail/CVE-2021-37666
- https://github.com/tensorflow/tensorflow/commit/be7a4de6adfbd303ce08be4332554dff70362612
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-579.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-777.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-288.yaml
- https://github.com/tensorflow/tensorflow
