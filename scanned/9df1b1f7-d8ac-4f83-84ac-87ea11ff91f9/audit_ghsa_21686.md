# [M] Memory leak in decoding PNG images

## Summary
Severity: Medium
Advisory: GHSA-fq6p-6334-8gr4
CVE: CVE-2022-23585
CWE: CWE-401
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-fq6p-6334-8gr4
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
When [decoding PNG images](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/kernels/image/decode_image_op.cc#L322-L416) TensorFlow can produce a memory leak if the image is invalid.
After calling `png::CommonInitDecode(..., &decode)`, the `decode` value contains allocated buffers which can only be freed by calling `png::CommonFreeDecode(&decode)`. However, several error case in the function implementation invoke the `OP_REQUIRES` macro which immediately terminates the execution of the function, without allowing for the memory free to occur.
  
### Patches   
We have patched the issue in GitHub commit [ab51e5b813573dc9f51efa335aebcf2994125ee9](https://github.com/tensorflow/tensorflow/commit/ab51e5b813573dc9f51efa335aebcf2994125ee9).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-fq6p-6334-8gr4
- https://nvd.nist.gov/vuln/detail/CVE-2022-23585
- https://github.com/tensorflow/tensorflow/commit/ab51e5b813573dc9f51efa335aebcf2994125ee9
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-94.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-149.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/kernels/image/decode_image_op.cc#L322-L416
