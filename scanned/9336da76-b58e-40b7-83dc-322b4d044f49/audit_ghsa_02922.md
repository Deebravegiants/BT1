# [M] Overflow/crash in `tf.range`

## Summary
Severity: Medium
Advisory: GHSA-xrqm-fpgr-6hhx
CVE: CVE-2021-41202
CWE: CWE-681
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-xrqm-fpgr-6hhx
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
While calculating the size of the output within the `tf.range` kernel, there is a conditional statement of type `int64 = condition ? int64 : double`. Due to C++ implicit conversion rules, both branches of the condition will be cast to `double` and the result would be truncated before the assignment. This result in overflows:

```python
import tensorflow as tf

tf.sparse.eye(num_rows=9223372036854775807, num_columns=None)
```
  
Similarly, `tf.range` would result in crashes due to overflows if the start or end point are too large.

```python
import tensorflow as tf

tf.range(start=-1e+38, limit=1)
```

### Patches
We have patched the issue in GitHub commits [6d94002a09711d297dbba90390d5482b76113899](https://github.com/tensorflow/tensorflow/commit/6d94002a09711d297dbba90390d5482b76113899) (merging [#51359](https://github.com/tensorflow/tensorflow/pull/51359)) and [1b0e0ec27e7895b9985076eab32445026ae5ca94](https://github.com/tensorflow/tensorflow/commit/1b0e0ec27e7895b9985076eab32445026ae5ca94) (merging [#51711](https://github.com/tensorflow/tensorflow/pull/51711)).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via [GitHub issue](https://github.com/tensorflow/tensorflow/issues/46912), [GitHub issue](https://github.com/tensorflow/tensorflow/issues/46899) and [GitHub issue](https://github.com/tensorflow/tensorflow/issues/46889).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xrqm-fpgr-6hhx
- https://nvd.nist.gov/vuln/detail/CVE-2021-41202
- https://github.com/tensorflow/tensorflow/issues/46889
- https://github.com/tensorflow/tensorflow/issues/46912
- https://github.com/tensorflow/tensorflow/commit/1b0e0ec27e7895b9985076eab32445026ae5ca94
- https://github.com/tensorflow/tensorflow/commit/6d94002a09711d297dbba90390d5482b76113899
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-612.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-810.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-395.yaml
- https://github.com/tensorflow/tensorflow
