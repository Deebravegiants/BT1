# [M] Segfault due to missing support for quantized types

## Summary
Severity: Medium
Advisory: GHSA-54ch-gjq5-4976
CVE: CVE-2022-29205
CWE: CWE-476, CWE-908
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-54ch-gjq5-4976
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.6.4
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.6.4
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.6.4
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1

## Details
### Impact
There is a potential for segfault / denial of service in TensorFlow by calling `tf.compat.v1.*` ops which don't yet have support for quantized types (added after migration to TF 2.x):

```python
import numpy as np
import tensorflow as tf

tf.compat.v1.placeholder_with_default(input=np.array([2]),shape=tf.constant(dtype=tf.qint8, value=np.array([1])))
```

In these scenarios, since the kernel is missing, a [`nullptr` value is passed](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/python/eager/pywrap_tfe_src.cc#L480-L482) to [`ParseDimensionValue`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/python/eager/pywrap_tfe_src.cc#L296-L320) for the `py_value` argument. Then, this is dereferenced, resulting in segfault.

### Patches
We have patched the issue in GitHub commit [237822b59fc504dda2c564787f5d3ad9c4aa62d9](https://github.com/tensorflow/tensorflow/commit/237822b59fc504dda2c564787f5d3ad9c4aa62d9).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Hong Jin from Singapore Management University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-54ch-gjq5-4976
- https://nvd.nist.gov/vuln/detail/CVE-2022-29205
- https://github.com/tensorflow/tensorflow/commit/237822b59fc504dda2c564787f5d3ad9c4aa62d9
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/python/eager/pywrap_tfe_src.cc#L296-L320
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/python/eager/pywrap_tfe_src.cc#L480-L482
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
