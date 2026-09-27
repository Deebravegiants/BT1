# [H] Segfault and heap buffer overflow in `{Experimental,}DatasetToTFRecord`

## Summary
Severity: High
Advisory: GHSA-f8h4-7rgh-q2gm
CVE: CVE-2021-37650
CWE: CWE-120, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-f8h4-7rgh-q2gm
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.3.4
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
The implementation for `tf.raw_ops.ExperimentalDatasetToTFRecord` and `tf.raw_ops.DatasetToTFRecord` can trigger heap buffer overflow and segmentation fault:

```python
import tensorflow as tf

dataset = tf.data.Dataset.range(3)
dataset = tf.data.experimental.to_variant(dataset)
tf.raw_ops.ExperimentalDatasetToTFRecord(
  input_dataset=dataset,
  filename='/tmp/output',
  compression_type='')
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/f24faa153ad31a4b51578f8181d3aaab77a1ddeb/tensorflow/core/kernels/data/experimental/to_tf_record_op.cc#L93-L102) assumes that all records in the dataset are of string type. However, there is no check for that, and the example given above uses numeric types.

### Patches
We have patched the issue in GitHub commit [e0b6e58c328059829c3eb968136f17aa72b6c876](https://github.com/tensorflow/tensorflow/commit/e0b6e58c328059829c3eb968136f17aa72b6c876).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-f8h4-7rgh-q2gm
- https://nvd.nist.gov/vuln/detail/CVE-2021-37650
- https://github.com/tensorflow/tensorflow/commit/e0b6e58c328059829c3eb968136f17aa72b6c876
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-563.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-761.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-272.yaml
- https://github.com/tensorflow/tensorflow
