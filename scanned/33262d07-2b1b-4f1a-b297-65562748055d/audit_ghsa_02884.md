# [M] Incomplete validation in `tf.summary.create_file_writer`

## Summary
Severity: Medium
Advisory: GHSA-gh8h-7j2j-qv4f
CVE: CVE-2021-41200
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-gh8h-7j2j-qv4f
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
If `tf.summary.create_file_writer` is called with non-scalar arguments code crashes due to a `CHECK`-fail.

```python
import tensorflow as tf
import numpy as np
tf.summary.create_file_writer(logdir='', flush_millis=np.ones((1,2)))
```

### Patches
We have patched the issue in GitHub commit [874bda09e6702cd50bac90b453b50bcc65b2769e](https://github.com/tensorflow/tensorflow/commit/874bda09e6702cd50bac90b453b50bcc65b2769e) (merging [#51715](https://github.com/tensorflow/tensorflow/pull/51715)).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/46909).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gh8h-7j2j-qv4f
- https://nvd.nist.gov/vuln/detail/CVE-2021-41200
- https://github.com/tensorflow/tensorflow/issues/46909
- https://github.com/tensorflow/tensorflow/commit/874bda09e6702cd50bac90b453b50bcc65b2769e
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-610.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-808.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-393.yaml
- https://github.com/tensorflow/tensorflow
