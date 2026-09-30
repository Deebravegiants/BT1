# [M] Incomplete validation in signal ops leads to crashes in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-5889-7v45-q28m
CVE: CVE-2022-29213
CWE: CWE-20, CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5889-7v45-q28m
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
The `tf.compat.v1.signal.rfft2d` and `tf.compat.v1.signal.rfft3d` lack input validation and under certain condition can result in crashes (due to `CHECK`-failures).

### Patches 
We have patched the issue in GitHub commit [0a8a781e597b18ead006d19b7d23d0a369e9ad73](https://github.com/tensorflow/tensorflow/commit/0a8a781e597b18ead006d19b7d23d0a369e9ad73) (merging GitHub PR [#55274](https://github.com/tensorflow/tensorflow/pull/55274)).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/55263).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5889-7v45-q28m
- https://nvd.nist.gov/vuln/detail/CVE-2022-29213
- https://github.com/tensorflow/tensorflow/issues/55263
- https://github.com/tensorflow/tensorflow/pull/55274
- https://github.com/tensorflow/tensorflow/commit/0a8a781e597b18ead006d19b7d23d0a369e9ad73
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
