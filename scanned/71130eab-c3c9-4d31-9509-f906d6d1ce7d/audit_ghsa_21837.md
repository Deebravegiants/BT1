# [H] Use after free in `DecodePng` kernel

## Summary
Severity: High
Advisory: GHSA-24x4-6qmh-88qg
CVE: CVE-2022-23584
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-24x4-6qmh-88qg
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
A malicious user can cause a use after free behavior when [decoding PNG images](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/kernels/image/decode_image_op.cc#L339-L346):
```cc
if (/* ... error conditions ... */) {
  png::CommonFreeDecode(&decode);
  OP_REQUIRES(context, false,
              errors::InvalidArgument("PNG size too large for int: ",
                                      decode.width, " by ", decode.height));
}   
```
After `png::CommonFreeDecode(&decode)` gets called, the values of `decode.width` and `decode.height` are in an unspecified state.

### Patches
We have patched the issue in GitHub commit [e746adbfcfee15e9cfdb391ff746c765b99bdf9b](https://github.com/tensorflow/tensorflow/commit/e746adbfcfee15e9cfdb391ff746c765b99bdf9b).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-24x4-6qmh-88qg
- https://nvd.nist.gov/vuln/detail/CVE-2022-23584
- https://github.com/tensorflow/tensorflow/commit/e746adbfcfee15e9cfdb391ff746c765b99bdf9b
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-93.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-148.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/kernels/image/decode_image_op.cc#L339-L346
