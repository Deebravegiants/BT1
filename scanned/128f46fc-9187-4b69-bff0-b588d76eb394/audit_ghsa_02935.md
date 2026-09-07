# [M] Crash in `max_pool3d` when size argument is 0 or negative

## Summary
Severity: Medium
Advisory: GHSA-m539-j985-hcr8
CVE: CVE-2021-41196
CWE: CWE-191
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-m539-j985-hcr8
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
The Keras pooling layers can trigger a segfault if the size of the pool is 0 or if a dimension is negative: 

```python
import tensorflow as tf

pool_size = [2, 2, 0]
layer = tf.keras.layers.MaxPooling3D(strides=1, pool_size=pool_size)
input_tensor = tf.random.uniform([3, 4, 10, 11, 12], dtype=tf.float32)
res = layer(input_tensor)
```

This is due to the TensorFlow's implementation of pooling operations where the values in the sliding window are not checked to be strictly positive.

### Patches
We have patched the issue in GitHub commit [12b1ff82b3f26ff8de17e58703231d5a02ef1b8b](https://github.com/tensorflow/tensorflow/commit/12b1ff82b3f26ff8de17e58703231d5a02ef1b8b) (merging [#51975](https://github.com/tensorflow/tensorflow/pull/51975)).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution 
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/51936).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-m539-j985-hcr8
- https://nvd.nist.gov/vuln/detail/CVE-2021-41196
- https://github.com/tensorflow/tensorflow/issues/51936
- https://github.com/tensorflow/tensorflow/commit/12b1ff82b3f26ff8de17e58703231d5a02ef1b8b
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-606.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-804.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-389.yaml
- https://github.com/tensorflow/tensorflow
