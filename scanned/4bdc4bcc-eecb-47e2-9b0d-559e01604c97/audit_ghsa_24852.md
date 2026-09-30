# [M] Type confusion leading to `CHECK`-failure based denial of service in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-f4rr-5m7v-wxcw
CVE: CVE-2022-29209
CWE: CWE-843
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f4rr-5m7v-wxcw
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
The [macros that TensorFlow uses for writing assertions (e.g., `CHECK_LT`, `CHECK_GT`, etc.)](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/platform/default/logging.h) have an incorrect logic when comparing `size_t` and `int` values. Due to type conversion rules, several of the macros would trigger incorrectly.

### Patches
We have patched the issue in GitHub commit [b917181c29b50cb83399ba41f4d938dc369109a1](https://github.com/tensorflow/tensorflow/commit/b917181c29b50cb83399ba41f4d938dc369109a1) (merging GitHub PR [#55730](https://github.com/tensorflow/tensorflow/pull/55730)).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/55530).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-f4rr-5m7v-wxcw
- https://nvd.nist.gov/vuln/detail/CVE-2022-29209
- https://github.com/tensorflow/tensorflow/issues/55530
- https://github.com/tensorflow/tensorflow/pull/55730
- https://github.com/tensorflow/tensorflow/commit/b917181c29b50cb83399ba41f4d938dc369109a1
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/platform/default/logging.h
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
