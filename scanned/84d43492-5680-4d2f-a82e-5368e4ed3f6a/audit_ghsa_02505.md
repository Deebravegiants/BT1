# [M] Division by 0 in inplace operations

## Summary
Severity: Medium
Advisory: GHSA-cm5x-837x-jf3c
CVE: CVE-2021-37660
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-cm5x-837x-jf3c
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
An attacker can cause a floating point exception by calling inplace operations with crafted arguments that would result in a division by 0:

```python
import tensorflow as tf

tf.raw_ops.InplaceSub(x=[],i=[-99,-1,-1],v=[1,1,1])
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/84d053187cb80d975ef2b9684d4b61981bca0c41/tensorflow/core/kernels/inplace_ops.cc#L283) has a logic error: it should skip processing if `x` and `v` are empty but the code uses `||` instead of `&&`.

### Patches
We have patched the issue in GitHub commit [e86605c0a336c088b638da02135ea6f9f6753618](https://github.com/tensorflow/tensorflow/commit/e86605c0a336c088b638da02135ea6f9f6753618).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cm5x-837x-jf3c
- https://nvd.nist.gov/vuln/detail/CVE-2021-37660
- https://github.com/tensorflow/tensorflow/commit/e86605c0a336c088b638da02135ea6f9f6753618
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-573.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-771.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-282.yaml
- https://github.com/tensorflow/tensorflow
