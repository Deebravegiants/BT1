# [M] Float cast overflow undefined behavior

## Summary
Severity: Medium
Advisory: GHSA-xwhf-g6j5-j5gc
CVE: CVE-2020-15266
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2020-11-13
Source: https://github.com/advisories/GHSA-xwhf-g6j5-j5gc
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.4.0
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.0
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.0

## Details
### Impact
When the `boxes` argument of `tf.image.crop_and_resize` has a very large value, the CPU kernel implementation receives it as a C++ `nan` floating point value. Attempting to operate on this is undefined behavior which later produces a segmentation fault.

### Patches

We have patched the issue in c0319231333f0f16e1cc75ec83660b01fedd4182 and will release TensorFlow 2.4.0 containing the patch. TensorFlow nightly packages after this commit will also have the issue resolved.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported in #42129

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xwhf-g6j5-j5gc
- https://nvd.nist.gov/vuln/detail/CVE-2020-15266
- https://github.com/tensorflow/tensorflow/issues/42129
- https://github.com/tensorflow/tensorflow/pull/42143/commits/3ade2efec2e90c6237de32a19680caaa3ebc2845
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-296.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-331.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-139.yaml
- https://github.com/tensorflow/tensorflow
