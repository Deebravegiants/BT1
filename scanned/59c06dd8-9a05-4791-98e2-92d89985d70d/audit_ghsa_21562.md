# [M] `MirrorPadGrad` heap out of bounds read

## Summary
Severity: Medium
Advisory: GHSA-gq2j-cr96-gvqx
CVE: CVE-2022-41895
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-gq2j-cr96-gvqx
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
If [`MirrorPadGrad`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/mirror_pad_op.cc) is given outsize input `paddings`, TensorFlow will give a heap OOB error.

```python
import tensorflow as tf
tf.raw_ops.MirrorPadGrad(input=[1],
             paddings=[[0x77f00000,0xa000000]],
             mode = 'REFLECT')
```

### Patches
We have patched the issue in GitHub commit [717ca98d8c3bba348ff62281fdf38dcb5ea1ec92](https://github.com/tensorflow/tensorflow/commit/717ca98d8c3bba348ff62281fdf38dcb5ea1ec92).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Vul AI.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gq2j-cr96-gvqx
- https://nvd.nist.gov/vuln/detail/CVE-2022-41895
- https://github.com/tensorflow/tensorflow/commit/717ca98d8c3bba348ff62281fdf38dcb5ea1ec92
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/mirror_pad_op.cc
