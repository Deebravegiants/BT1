# [M] Heap buffer overflow in `Transpose`

## Summary
Severity: Medium
Advisory: GHSA-3ff2-r28g-w7h9
CVE: CVE-2021-41216
CWE: CWE-120, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-3ff2-r28g-w7h9
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
The [shape inference function for `Transpose`](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/ops/array_ops.cc#L121-L185) is vulnerable to a heap buffer overflow:

```python
import tensorflow as tf
@tf.function
def test():
  y = tf.raw_ops.Transpose(x=[1,2,3,4],perm=[-10])
  return y

test()
```

This occurs whenever `perm` contains negative elements. The shape inference function does not validate that the indices in `perm` are all valid:
        
```cc
for (int32_t i = 0; i < rank; ++i) {
  int64_t in_idx = data[i];
  if (in_idx >= rank) {
    return errors::InvalidArgument("perm dim ", in_idx,
                                   " is out of range of input rank ", rank);
  }
  dims[i] = c->Dim(input, in_idx);
}
```

where `Dim(tensor, index)` accepts either a positive index less than the rank of the tensor or the special value `-1` for unknown dimensions.

### Patches
We have patched the issue in GitHub commit [c79ba87153ee343401dbe9d1954d7f79e521eb14](https://github.com/tensorflow/tensorflow/commit/c79ba87153ee343401dbe9d1954d7f79e521eb14).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-3ff2-r28g-w7h9
- https://nvd.nist.gov/vuln/detail/CVE-2021-41216
- https://github.com/tensorflow/tensorflow/commit/c79ba87153ee343401dbe9d1954d7f79e521eb14
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-625.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-823.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-408.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/ops/array_ops.cc#L121-L185
