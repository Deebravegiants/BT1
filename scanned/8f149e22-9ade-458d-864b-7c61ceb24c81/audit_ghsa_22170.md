# [M] Segfault if `tf.histogram_fixed_width` is called with NaN values in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-xrp2-fhq4-4q3w
CVE: CVE-2022-29211
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xrp2-fhq4-4q3w
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
The implementation of [`tf.histogram_fixed_width`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/histogram_op.cc) is vulnerable to a crash when the values array contain `NaN` elements:

```python
import tensorflow as tf
import numpy as np

tf.histogram_fixed_width(values=np.nan, value_range=[1,2])
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/histogram_op.cc#L35-L74) assumes that all floating point operations are defined and then converts a floating point result to an integer index:

```cc
index_to_bin.device(d) =
    ((values.cwiseMax(value_range(0)) - values.constant(value_range(0)))
         .template cast<double>() /
     step)
        .cwiseMin(nbins_minus_1)
        .template cast<int32>();
```

If `values` contains `NaN` then the result of the division is still `NaN` and the cast to `int32` would result in a crash.

This only occurs on the CPU implementation.

### Patches
We have patched the issue in GitHub commit [e57fd691c7b0fd00ea3bfe43444f30c1969748b5](https://github.com/tensorflow/tensorflow/commit/e57fd691c7b0fd00ea3bfe43444f30c1969748b5).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/45770).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xrp2-fhq4-4q3w
- https://nvd.nist.gov/vuln/detail/CVE-2022-29211
- https://github.com/tensorflow/tensorflow/issues/45770
- https://github.com/tensorflow/tensorflow/commit/e57fd691c7b0fd00ea3bfe43444f30c1969748b5
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/histogram_op.cc
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/histogram_op.cc#L35-L74
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
