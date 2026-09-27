# [H] TensorFlow vulnerable to OOB write in `scatter_nd` in TF Lite

## Summary
Severity: High
Advisory: GHSA-ffjm-4qwc-7cmf
CVE: CVE-2022-35939
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-ffjm-4qwc-7cmf
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1

## Details
### Impact
The [`ScatterNd`](https://github.com/tensorflow/tensorflow/blob/266558ac4c1f361e9a178ee9d3f0ce2e648ae499/tensorflow/lite/kernels/internal/reference/reference_ops.h#L659-L698) function takes an input argument that determines the indices of of the output tensor. An input index greater than the output tensor or less than zero will either write content at the wrong index or trigger a crash.

### Patches
We have patched the issue in GitHub commit [b4d4b4cb019bd7240a52daa4ba61e3cc814f0384](https://github.com/tensorflow/tensorflow/commit/b4d4b4cb019bd7240a52daa4ba61e3cc814f0384).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Hui Peng from Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-ffjm-4qwc-7cmf
- https://nvd.nist.gov/vuln/detail/CVE-2022-35939
- https://github.com/tensorflow/tensorflow/commit/b4d4b4cb019bd7240a52daa4ba61e3cc814f0384
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/266558ac4c1f361e9a178ee9d3f0ce2e648ae499/tensorflow/lite/kernels/internal/reference/reference_ops.h#L659-L698
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
