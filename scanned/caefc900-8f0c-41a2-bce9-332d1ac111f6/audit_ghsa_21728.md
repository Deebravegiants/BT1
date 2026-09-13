# [M] Null pointer dereference in Grappler's `IsConstant`

## Summary
Severity: Medium
Advisory: GHSA-9px9-73fg-3fqp
CVE: CVE-2022-23589
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-9px9-73fg-3fqp
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact
Under certain scenarios, Grappler component of TensorFlow can trigger a null pointer dereference. There are 2 places where this can occur, for the same malicious alteration of a `SavedModel` file (fixing the first one would trigger the same dereference in the second place):

First, during [constant folding](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/optimizers/constant_folding.cc#L3466-L3497), the `GraphDef` might not have the required nodes for the binary operation:

```cc
  NodeDef* mul_left_child = node_map_->GetNode(node->input(0));
  NodeDef* mul_right_child = node_map_->GetNode(node->input(1));
  // One child must be constant, and the second must be Conv op.
  const bool left_child_is_constant = IsReallyConstant(*mul_left_child);
  const bool right_child_is_constant = IsReallyConstant(*mul_right_child);
```

If a node is missing, the correposning `mul_*child` would be null, and the dereference in the subsequent line would be incorrect.

We have a similar issue during [`IsIdentityConsumingSwitch`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/mutable_graph_view.cc#L59-L74):

```cc
  NodeDef* input_node = graph.GetNode(tensor_id.node());
  return IsSwitch(*input_node);
```

### Patches
We have patched the issue in GitHub commits [0a365c029e437be0349c31f8d4c9926b69fa3fa1](https://github.com/tensorflow/tensorflow/commit/0a365c029e437be0349c31f8d4c9926b69fa3fa1) and [045deec1cbdebb27d817008ad5df94d96a08b1bf](https://github.com/tensorflow/tensorflow/commit/045deec1cbdebb27d817008ad5df94d96a08b1bf).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9px9-73fg-3fqp
- https://nvd.nist.gov/vuln/detail/CVE-2022-23589
- https://github.com/tensorflow/tensorflow/commit/045deec1cbdebb27d817008ad5df94d96a08b1bf
- https://github.com/tensorflow/tensorflow/commit/0a365c029e437be0349c31f8d4c9926b69fa3fa1
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-98.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-153.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/mutable_graph_view.cc#L59-L74
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/optimizers/constant_folding.cc#L3466-L3497
