# [M] Missing validation causes denial of service via `UnsortedSegmentJoin`

## Summary
Severity: Medium
Advisory: GHSA-hrg5-737c-2p56
CVE: CVE-2022-29197
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hrg5-737c-2p56
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
The implementation of [`tf.raw_ops.UnsortedSegmentJoin`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/unsorted_segment_join_op.cc#L92-L95) does not fully validate the input arguments. This results in a `CHECK`-failure which can be used to trigger a denial of service attack:

```python
import tensorflow as tf

tf.raw_ops.UnsortedSegmentJoin(
  inputs=tf.constant("this", shape=[12], dtype=tf.string),
  segment_ids=tf.constant(0, shape=[12], dtype=tf.int64),
  num_segments=tf.constant(0, shape=[12], dtype=tf.int64))
``` 
  
The code assumes `num_segments` is a scalar but there is no validation for this before accessing its value:

```cc
const Tensor& num_segments_tensor = context->input(2);
OP_REQUIRES(context, num_segments_tensor.NumElements() != 0,
            errors::InvalidArgument("Number of segments cannot be empty."));
auto num_segments = num_segments_tensor.scalar<NUM_SEGMENTS_TYPE>()();
``` 

### Patches
We have patched the issue in GitHub commit [13d38a07ce9143e044aa737cfd7bb759d0e9b400](https://github.com/tensorflow/tensorflow/commit/13d38a07ce9143e044aa737cfd7bb759d0e9b400).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Neophytos Christou from Secure Systems Lab at Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hrg5-737c-2p56
- https://nvd.nist.gov/vuln/detail/CVE-2022-29197
- https://github.com/tensorflow/tensorflow/commit/13d38a07ce9143e044aa737cfd7bb759d0e9b400
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/unsorted_segment_join_op.cc#L92-L95
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
