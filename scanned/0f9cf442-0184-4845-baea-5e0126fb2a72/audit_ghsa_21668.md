# [H] Read and Write outside of bounds in TensorFlow

## Summary
Severity: High
Advisory: GHSA-4hvf-hxvg-f67v
CVE: CVE-2022-23560
CWE: CWE-125, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-4hvf-hxvg-f67v
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact
An attacker can craft a TFLite model that would allow limited reads and writes outside of arrays in TFLite. This exploits missing validation in [the conversion from sparse tensors to dense tensors](https://github.com/tensorflow/tensorflow/blob/ca6f96b62ad84207fbec580404eaa7dd7403a550/tensorflow/lite/kernels/internal/utils/sparsity_format_converter.cc#L252-L293).

### Patches
We have patched the issue in GitHub commit [6364463d6f5b6254cac3d6aedf999b6a96225038](https://github.com/tensorflow/tensorflow/commit/6364463d6f5b6254cac3d6aedf999b6a96225038).
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Wang Xuan of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4hvf-hxvg-f67v
- https://nvd.nist.gov/vuln/detail/CVE-2022-23560
- https://github.com/tensorflow/tensorflow/commit/6364463d6f5b6254cac3d6aedf999b6a96225038
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-69.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-124.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/ca6f96b62ad84207fbec580404eaa7dd7403a550/tensorflow/lite/kernels/internal/utils/sparsity_format_converter.cc#L252-L293
