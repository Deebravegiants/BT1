# [M] Tensorflow vulnerable to Out-of-Bounds Read

## Summary
Severity: Medium
Advisory: GHSA-8w5g-3wcv-9g2j
CVE: CVE-2022-41880
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-11-22
Source: https://github.com/advisories/GHSA-8w5g-3wcv-9g2j
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3

## Details
### Impact
When the [`BaseCandidateSamplerOp`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/candidate_sampler_ops.cc) function  receives a value in `true_classes` larger than `range_max`, a heap oob vuln occurs.
```python
tf.raw_ops.ThreadUnsafeUnigramCandidateSampler(
    true_classes=[[0x100000,1]],
    num_true = 2,
    num_sampled = 2,
    unique = False,
    range_max = 2,
    seed = 2,
    seed2 = 2)
```

### Patches
We have patched the issue in GitHub commit [b389f5c944cadfdfe599b3f1e4026e036f30d2d4](https://github.com/tensorflow/tensorflow/commit/b389f5c944cadfdfe599b3f1e4026e036f30d2d4).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Yu Tian of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-8w5g-3wcv-9g2j
- https://nvd.nist.gov/vuln/detail/CVE-2022-41880
- https://github.com/tensorflow/tensorflow/commit/b389f5c944cadfdfe599b3f1e4026e036f30d2d4
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/candidate_sampler_ops.cc
