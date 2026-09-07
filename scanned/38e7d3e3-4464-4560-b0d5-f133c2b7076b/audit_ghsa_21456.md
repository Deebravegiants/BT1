# [M] FPE in `tf.image.generate_bounding_box_proposals`

## Summary
Severity: Medium
Advisory: GHSA-6x99-gv2v-q76v
CVE: CVE-2022-41888
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-6x99-gv2v-q76v
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
When running on GPU, [`tf.image.generate_bounding_box_proposals`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/generate_box_proposals_op.cu.cc) receives a `scores` input that must be of rank 4 but is not checked.
```python
import tensorflow as tf

a = tf.constant(value=[[1.0, 1.0], [1.0, 1.0], [1.0, 1.0], [1.0, 1.0]])
b = tf.constant(value=[1])

tf.image.generate_bounding_box_proposals(scores=a,bbox_deltas=a,image_info=a,anchors=a,pre_nms_topn=b)
```

### Patches
We have patched the issue in GitHub commit [cf35502463a88ca7185a99daa7031df60b3c1c98](https://github.com/tensorflow/tensorflow/commit/cf35502463a88ca7185a99daa7031df60b3c1c98).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Pattarakrit Rattankul.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-6x99-gv2v-q76v
- https://nvd.nist.gov/vuln/detail/CVE-2022-41888
- https://github.com/tensorflow/tensorflow/commit/cf35502463a88ca7185a99daa7031df60b3c1c98
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/generate_box_proposals_op.cu.cc
