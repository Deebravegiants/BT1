# [H] Use after free in boosted trees creation

## Summary
Severity: High
Advisory: GHSA-m7fm-4jfh-jrg6
CVE: CVE-2021-37652
CWE: CWE-415, CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-m7fm-4jfh-jrg6
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
The implementation for `tf.raw_ops.BoostedTreesCreateEnsemble` can result in a use after free error if an attacker supplies specially crafted arguments:

```python
import tensorflow as tf

v= tf.Variable([0.0])
tf.raw_ops.BoostedTreesCreateEnsemble(
  tree_ensemble_handle=v.handle,
  stamp_token=[0],
  tree_ensemble_serialized=['0']) 
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/f24faa153ad31a4b51578f8181d3aaab77a1ddeb/tensorflow/core/kernels/boosted_trees/resource_ops.cc#L55) uses a reference counted resource and decrements the refcount if the initialization fails, as it should. However, when the code was written, the  resource was represented as a naked pointer but later refactoring has changed it to be a smart pointer. Thus, when the pointer leaves the scope, a subsequent `free`-ing of the resource occurs, but this fails to take into account that the refcount has already reached 0, thus the resource has been already freed. During this double-free process, members of the resource object are accessed for cleanup but they are invalid as the entire resource has been freed.

### Patches
We have patched the issue in GitHub commit [5ecec9c6fbdbc6be03295685190a45e7eee726ab](https://github.com/tensorflow/tensorflow/commit/5ecec9c6fbdbc6be03295685190a45e7eee726ab).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-m7fm-4jfh-jrg6
- https://nvd.nist.gov/vuln/detail/CVE-2021-37652
- https://github.com/tensorflow/tensorflow/commit/5ecec9c6fbdbc6be03295685190a45e7eee726ab
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-565.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-763.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-274.yaml
- https://github.com/tensorflow/tensorflow
