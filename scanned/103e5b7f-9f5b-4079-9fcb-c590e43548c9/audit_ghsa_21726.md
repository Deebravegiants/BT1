# [H] Assertion failure based denial of service in Tensorflow

## Summary
Severity: High
Advisory: GHSA-f2vv-v9cg-qhh7
CVE: CVE-2022-21737
CWE: CWE-617, CWE-754
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-f2vv-v9cg-qhh7
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
The [implementation of `*Bincount` operations](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/bincount_op.cc) allows malicious users to cause denial of service by passing in arguments which would trigger a `CHECK`-fail:

```python
import tensorflow as tf

tf.raw_ops.DenseBincount(
  input=[[0], [1], [2]],
  size=[1],
  weights=[3,2,1],
  binary_output=False)
```

There are several conditions that the input arguments must satisfy. Some are not caught during shape inference and others are not caught during kernel implementation. This results in `CHECK` failures later when the output tensors get allocated.

### Patches
We have patched the issue in GitHub commit [7019ce4f68925fd01cdafde26f8d8c938f47e6f9](https://github.com/tensorflow/tensorflow/commit/7019ce4f68925fd01cdafde26f8d8c938f47e6f9).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Faysal Hossain Shezan from University of Virginia.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-f2vv-v9cg-qhh7
- https://nvd.nist.gov/vuln/detail/CVE-2022-21737
- https://github.com/tensorflow/tensorflow/commit/7019ce4f68925fd01cdafde26f8d8c938f47e6f9
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-61.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-116.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/bincount_op.cc
