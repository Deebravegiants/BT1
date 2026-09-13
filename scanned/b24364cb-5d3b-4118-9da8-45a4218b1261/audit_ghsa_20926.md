# [M] TensorFlow vulnerable to Int overflow in `RaggedRangeOp`

## Summary
Severity: Medium
Advisory: GHSA-x989-q2pq-4q5x
CVE: CVE-2022-35940
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-x989-q2pq-4q5x
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1

## Details
### Impact
The [`RaggedRangOp`](https://github.com/tensorflow/tensorflow/blob/0b6b491d21d6a4eb5fbab1cca565bc1e94ca9543/tensorflow/core/kernels/ragged_range_op.cc#L74-L88) function takes an argument `limits` that is eventually used to construct a `TensorShape` as an `int64`. If `limits` is a very large float, it can overflow when converted to an `int64`. This triggers an `InvalidArgument` but also throws an abort signal that crashes the program.
```python
import tensorflow as tf
tf.raw_ops.RaggedRange(starts=[1.1,0.1],limits=[10.0,1e20],deltas=[1,1])
```

### Patches
We have patched the issue in GitHub commit [37cefa91bee4eace55715eeef43720b958a01192](https://github.com/tensorflow/tensorflow/commit/37cefa91bee4eace55715eeef43720b958a01192).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Jingyi Shi.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-x989-q2pq-4q5x
- https://nvd.nist.gov/vuln/detail/CVE-2022-35940
- https://github.com/tensorflow/tensorflow/commit/37cefa91bee4eace55715eeef43720b958a01192
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/0b6b491d21d6a4eb5fbab1cca565bc1e94ca9543/tensorflow/core/kernels/ragged_range_op.cc#L74-L88
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
