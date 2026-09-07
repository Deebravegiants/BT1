# [M] Integer division by 0 in `tf.raw_ops.AllToAll`

## Summary
Severity: Medium
Advisory: GHSA-9crf-c6qr-r273
CVE: CVE-2021-41218
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-9crf-c6qr-r273
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
The [shape inference code for `AllToAll`](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/ops/tpu_cross_replica_ops.cc#L25-L74) can be made to execute a division by 0:

```python
import tensorflow as tf
  
@tf.function
def func():
  return tf.raw_ops.AllToAll(
    input=[0.0, 0.1652, 0.6543],
    group_assignment=[1, -1],
    concat_dimension=0,
    split_dimension=0,
    split_count=0)

func()
```

This occurs whenever the `split_count` argument is 0:
  
```cc
TF_RETURN_IF_ERROR(c->GetAttr("split_count", &split_count));
...                  
for (int32_t i = 0; i < rank; ++i) {      
  ...                                     
  dims[i] = c->MakeDim(c->Value(dims[i]) / split_count);
  ...                
}
```

### Patches
We have patched the issue in GitHub commit [a8ad3e5e79c75f36edb81e0ba3f3c0c5442aeddc](https://github.com/tensorflow/tensorflow/commit/a8ad3e5e79c75f36edb81e0ba3f3c0c5442aeddc).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9crf-c6qr-r273
- https://nvd.nist.gov/vuln/detail/CVE-2021-41218
- https://github.com/tensorflow/tensorflow/commit/a8ad3e5e79c75f36edb81e0ba3f3c0c5442aeddc
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-627.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-825.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-410.yaml
- https://github.com/tensorflow/tensorflow
