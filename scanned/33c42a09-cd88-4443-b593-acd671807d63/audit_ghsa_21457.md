# [M] Segfault in `tf.raw_ops.TensorListConcat`

## Summary
Severity: Medium
Advisory: GHSA-66vq-54fq-6jvv
CVE: CVE-2022-41891
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-66vq-54fq-6jvv
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
If [`tf.raw_ops.TensorListConcat`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/list_kernels.h) is given `element_shape=[]`, it results segmentation fault which can be used to trigger a denial of service attack.
```python
import tensorflow as tf
tf.raw_ops.TensorListConcat(
    input_handle=tf.data.experimental.to_variant(tf.data.Dataset.from_tensor_slices([1, 2, 3])),
    element_dtype=tf.dtypes.float32,
    element_shape=[]
)
```

### Patches
We have patched the issue in GitHub commit [fc33f3dc4c14051a83eec6535b608abe1d355fde](https://github.com/tensorflow/tensorflow/commit/fc33f3dc4c14051a83eec6535b608abe1d355fde).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Tong Liu, ShanghaiTech University

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-66vq-54fq-6jvv
- https://nvd.nist.gov/vuln/detail/CVE-2022-41891
- https://github.com/tensorflow/tensorflow/commit/fc33f3dc4c14051a83eec6535b608abe1d355fde
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/list_kernels.h
