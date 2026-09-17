# [H] Null pointer dereference in `CompressElement`

## Summary
Severity: High
Advisory: GHSA-c9qf-r67m-p7cg
CVE: CVE-2021-37637
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-c9qf-r67m-p7cg
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
It is possible to trigger a null pointer dereference in TensorFlow by passing an invalid input to `tf.raw_ops.CompressElement`:

```python
import tensorflow as tf

tf.raw_ops.CompressElement(components=[[]])
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/47a06f40411a69c99f381495f490536972152ac0/tensorflow/core/data/compression_utils.cc#L34) was accessing the size of a buffer obtained from the return of a separate function call before validating that said buffer is valid.

### Patches
We have patched the issue in GitHub commit [5dc7f6981fdaf74c8c5be41f393df705841fb7c5](https://github.com/tensorflow/tensorflow/commit/5dc7f6981fdaf74c8c5be41f393df705841fb7c5).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for  more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360. Concurrently, it was resolved in `master` branch as it was also discovered internally and fixed before the report was handled.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-c9qf-r67m-p7cg
- https://nvd.nist.gov/vuln/detail/CVE-2021-37637
- https://github.com/tensorflow/tensorflow/commit/5dc7f6981fdaf74c8c5be41f393df705841fb7c5
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-550.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-748.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-259.yaml
- https://github.com/tensorflow/tensorflow
