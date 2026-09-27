# [M] Null pointer exception in `DeserializeSparse`

## Summary
Severity: Medium
Advisory: GHSA-x3v8-c8qx-3j3r
CVE: CVE-2021-41215
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-x3v8-c8qx-3j3r
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
The [shape inference code for `DeserializeSparse`](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/ops/sparse_ops.cc#L152-L168) can trigger a null pointer dereference:

```python
import tensorflow as tf

dataset = tf.data.Dataset.range(3)
  
@tf.function                 
def test():                  
  y = tf.raw_ops.DeserializeSparse(
    serialized_sparse=tf.data.experimental.to_variant(dataset),
    dtype=tf.int32)

test()
```

This is because the shape inference function assumes that the `serialize_sparse` tensor is a tensor with positive rank (and having `3` as the last dimension).  However, in the example above, the argument is a scalar (i.e., rank 0).

### Patches
We have patched the issue in GitHub commit [d3738dd70f1c9ceb547258cbb82d853da8771850](https://github.com/tensorflow/tensorflow/commit/d3738dd70f1c9ceb547258cbb82d853da8771850).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-x3v8-c8qx-3j3r
- https://nvd.nist.gov/vuln/detail/CVE-2021-41215
- https://github.com/tensorflow/tensorflow/commit/d3738dd70f1c9ceb547258cbb82d853da8771850
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-624.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-822.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-407.yaml
- https://github.com/tensorflow/tensorflow
