# [M] FPE in `ParallelConcat`

## Summary
Severity: Medium
Advisory: GHSA-7v94-64hj-m82h
CVE: CVE-2021-41207
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-7v94-64hj-m82h
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1

## Details
### Impact
The [implementation of `ParallelConcat`](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/inplace_ops.cc#L72-L97) misses some input validation and can produce a division by 0:

```python
import tensorflow as tf

@tf.function
def test():
  y = tf.raw_ops.ParallelConcat(values=[['tf']],shape=0)
  return y

test()
```

### Patches
We have patched the issue in GitHub commit [f2c3931113eaafe9ef558faaddd48e00a6606235](https://github.com/tensorflow/tensorflow/commit/f2c3931113eaafe9ef558faaddd48e00a6606235).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-7v94-64hj-m82h
- https://nvd.nist.gov/vuln/detail/CVE-2021-41207
- https://github.com/tensorflow/tensorflow/commit/9de11bdc2cf1284b2f635419bd3e6bbc7643eb2c
- https://github.com/tensorflow/tensorflow/commit/d11f21bbdfa54f3576ae860fc927bf23c675ebc0
- https://github.com/tensorflow/tensorflow/commit/e67caccea81167402c62977b5c521f2a8b261d6a
- https://github.com/tensorflow/tensorflow/commit/f2c3931113eaafe9ef558faaddd48e00a6606235
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-616.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-814.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-399.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/inplace_ops.cc#L72-L97
