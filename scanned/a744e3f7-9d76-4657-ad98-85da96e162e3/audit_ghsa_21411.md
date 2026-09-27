# [H] Out of bounds write in grappler in Tensorflow

## Summary
Severity: High
Advisory: GHSA-cg88-rpvp-cjv5
CVE: CVE-2022-41902
CWE: CWE-125, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-cg88-rpvp-cjv5
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
The function [MakeGrapplerFunctionItem](https://https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/grappler/utils/functions.cc#L221) takes arguments that determine the sizes of inputs and outputs. If the inputs given are greater than or equal to the sizes of the outputs, an out-of-bounds memory read or a crash is triggered.

### Patches
We have patched the issue in GitHub commit [a65411a1d69edfb16b25907ffb8f73556ce36bb7](https://github.com/tensorflow/tensorflow/commit/a65411a1d69edfb16b25907ffb8f73556ce36bb7).

The fix will be included in TensorFlow 2.11.0. We will also cherrypick this commit on TensorFlow 2.10.1.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cg88-rpvp-cjv5
- https://nvd.nist.gov/vuln/detail/CVE-2022-41902
- https://github.com/tensorflow/tensorflow/commit/a65411a1d69edfb16b25907ffb8f73556ce36bb7
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/grappler/utils/functions.cc#L221
