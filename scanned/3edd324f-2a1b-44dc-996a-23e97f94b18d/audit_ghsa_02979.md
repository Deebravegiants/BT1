# [M] Null pointer exception when `Exit` node is not preceded by `Enter` op

## Summary
Severity: Medium
Advisory: GHSA-5crj-c72x-m7gq
CVE: CVE-2021-41217
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-5crj-c72x-m7gq
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
The [process of building the control flow graph](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/common_runtime/immutable_executor_state.cc#L284-L346) for a TensorFlow model is vulnerable to a null pointer exception when nodes that should be paired are not:
  
```python
import tensorflow as tf
  
@tf.function
def func():
  return tf.raw_ops.Exit(data=[False,False])
    
func()
```

This occurs because the code assumes that the first node in the pairing (e.g., an `Enter` node) always exists when encountering the second node (e.g., an `Exit` node):
  
```cc
  ...
} else if (IsExit(curr_node)) {
  // Exit to the parent frame.
  parent = parent_nodes[curr_id];         
  frame_name = cf_info->frame_names[parent->id()];
  ...                
```

When this is not the case, `parent` is `nullptr` so dereferencing it causes a crash.

### Patches
We have patched the issue in GitHub commit [05cbebd3c6bb8f517a158b0155debb8df79017ff](https://github.com/tensorflow/tensorflow/commit/05cbebd3c6bb8f517a158b0155debb8df79017ff).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5crj-c72x-m7gq
- https://nvd.nist.gov/vuln/detail/CVE-2021-41217
- https://github.com/tensorflow/tensorflow/commit/05cbebd3c6bb8f517a158b0155debb8df79017ff
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-626.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-824.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-409.yaml
- https://github.com/tensorflow/tensorflow
