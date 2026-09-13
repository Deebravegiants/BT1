# [M] Memory exhaustion in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-c582-c96p-r5cq
CVE: CVE-2022-21732
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-c582-c96p-r5cq
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
The [implementation of `ThreadPoolHandle`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/data/experimental/threadpool_dataset_op.cc#L79-L135) can be used to trigger a denial of service attack by allocating too much memory:

```python
import tensorflow as tf
y = tf.raw_ops.ThreadPoolHandle(num_threads=0x60000000,display_name='tf')
```

This is because the `num_threads` argument is only checked to not be negative, but there is no upper bound on its value.
    
### Patches
We have patched the issue in GitHub commit [e3749a6d5d1e8d11806d4a2e9cc3123d1a90b75e](https://github.com/tensorflow/tensorflow/commit/e3749a6d5d1e8d11806d4a2e9cc3123d1a90b75e).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yu Tian of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-c582-c96p-r5cq
- https://nvd.nist.gov/vuln/detail/CVE-2022-21732
- https://github.com/tensorflow/tensorflow/commit/e3749a6d5d1e8d11806d4a2e9cc3123d1a90b75e
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-56.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-111.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/data/experimental/threadpool_dataset_op.cc#L79-L135
