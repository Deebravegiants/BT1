# [M] A use of uninitialized value vulnerability in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-7r94-xv9v-63jw
CVE: CVE-2021-41225
CWE: CWE-908
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-7r94-xv9v-63jw
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
TensorFlow's Grappler optimizer has a [use of unitialized variable](https://github.com/tensorflow/tensorflow/blob/3457a2b122e50b4d44ceaaed5a663d635e5c22df/tensorflow/core/grappler/optimizers/auto_parallel.cc#L155-L164):

```cc
  const NodeDef* dequeue_node;
  for (const auto& train_node : train_nodes) {
    if (IsDequeueOp(*train_node)) {
      dequeue_node = train_node;
      break;
    }
  }

  if (dequeue_node) {
    ...
  }
```

If the `train_nodes` vector (obtained from the saved model that gets optimized) does not contain a `Dequeue` node, then `dequeue_node` is left unitialized.

### Patches
We have patched the issue in GitHub commit [68867bf01239d9e1048f98cbad185bf4761bedd3](https://github.com/tensorflow/tensorflow/commit/68867bf01239d9e1048f98cbad185bf4761bedd3).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Qian Feng from Baidu Security Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-7r94-xv9v-63jw
- https://nvd.nist.gov/vuln/detail/CVE-2021-41225
- https://github.com/tensorflow/tensorflow/commit/68867bf01239d9e1048f98cbad185bf4761bedd3
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-634.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-832.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-417.yaml
- https://github.com/tensorflow/tensorflow
