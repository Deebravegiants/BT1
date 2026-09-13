# [M] Core dump when loading TFLite models with quantization in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-8wwm-6264-x792
CVE: CVE-2022-29212
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8wwm-6264-x792
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
Certain TFLite models that were created using TFLite model converter would crash when loaded in the TFLite interpreter. The culprit is that during quantization the scale of values could be greater than 1 but code was always assuming sub-unit scaling.

Thus, since code was calling [`QuantizeMultiplierSmallerThanOneExp`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/lite/kernels/internal/quantization_util.cc#L114-L123), the `TFLITE_CHECK_LT` assertion would trigger and abort the process.

### Patches
We have patched the issue in GitHub commit [a989426ee1346693cc015792f11d715f6944f2b8](https://github.com/tensorflow/tensorflow/commit/a989426ee1346693cc015792f11d715f6944f2b8).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/43661).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-8wwm-6264-x792
- https://nvd.nist.gov/vuln/detail/CVE-2022-29212
- https://github.com/tensorflow/tensorflow/issues/43661
- https://github.com/tensorflow/tensorflow/commit/a989426ee1346693cc015792f11d715f6944f2b8
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/lite/kernels/internal/quantization_util.cc#L114-L123
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
