# [M] Heap OOB in `SparseBinCount`

## Summary
Severity: Medium
Advisory: GHSA-374m-jm66-3vj8
CVE: CVE-2021-41226
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-374m-jm66-3vj8
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
The [implementation](https://github.com/tensorflow/tensorflow/blob/e71b86d47f8bc1816bf54d7bddc4170e47670b97/tensorflow/core/kernels/bincount_op.cc#L353-L417) of `SparseBinCount` is vulnerable to a heap OOB:

```python
import tensorflow as tf
  
  
tf.raw_ops.SparseBincount(
  indices=[[0],[1],[2]]
  values=[0,-10000000]
  dense_shape=[1,1]
  size=[1]
  weights=[3,2,1]
  binary_output=False)
```

This is because of missing validation between the elements of the `values` argument and the shape of the sparse output:


```cc
for (int64_t i = 0; i < indices_mat.dimension(0); ++i) {
  const int64_t batch = indices_mat(i, 0);
  const Tidx bin = values(i);
  ...
  out(batch, bin) = ...;
}
```

### Patches
We have patched the issue in GitHub commit [f410212e373eb2aec4c9e60bf3702eba99a38aba](https://github.com/tensorflow/tensorflow/commit/f410212e373eb2aec4c9e60bf3702eba99a38aba).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-374m-jm66-3vj8
- https://nvd.nist.gov/vuln/detail/CVE-2021-41226
- https://github.com/tensorflow/tensorflow/commit/f410212e373eb2aec4c9e60bf3702eba99a38aba
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-635.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-833.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-418.yaml
- https://github.com/tensorflow/tensorflow
