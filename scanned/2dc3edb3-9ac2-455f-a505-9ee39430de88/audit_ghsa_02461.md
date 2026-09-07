# [H] Null pointer dereference in `UncompressElement`

## Summary
Severity: High
Advisory: GHSA-6gv8-p3vj-pxvr
CVE: CVE-2021-37649
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-6gv8-p3vj-pxvr
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
The code for `tf.raw_ops.UncompressElement` can be made to trigger a null pointer dereference: 

```python
import tensorflow as tf

data = tf.data.Dataset.from_tensors([0.0])
tf.raw_ops.UncompressElement(
  compressed=tf.data.experimental.to_variant(data),
  output_types=[tf.int64],
  output_shapes=[2])
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/f24faa153ad31a4b51578f8181d3aaab77a1ddeb/tensorflow/core/kernels/data/experimental/compression_ops.cc#L50-L53) obtains a pointer to a `CompressedElement` from a `Variant` tensor and then proceeds to dereference it for decompressing. There is no check that the `Variant` tensor contained a `CompressedElement`, so the pointer is actually `nullptr`.

### Patches
We have patched the issue in GitHub commit [7bdf50bb4f5c54a4997c379092888546c97c3ebd](https://github.com/tensorflow/tensorflow/commit/7bdf50bb4f5c54a4997c379092888546c97c3ebd).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-6gv8-p3vj-pxvr
- https://nvd.nist.gov/vuln/detail/CVE-2021-37649
- https://github.com/tensorflow/tensorflow/commit/7bdf50bb4f5c54a4997c379092888546c97c3ebd
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-562.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-760.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-271.yaml
- https://github.com/tensorflow/tensorflow
