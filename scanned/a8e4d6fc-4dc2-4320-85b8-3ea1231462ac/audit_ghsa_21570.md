# [M] Invalid char to bool conversion when printing a tensor

## Summary
Severity: Medium
Advisory: GHSA-pf36-r9c6-h97j
CVE: CVE-2022-41911
CWE: CWE-704
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-pf36-r9c6-h97j
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
When [printing a tensor](https://github.com/tensorflow/tensorflow/blob/807cae8a807960fd7ac2313cde73a11fc15e7942/tensorflow/core/framework/tensor.cc#L1200-L1227), we get it's data as a `const char*` array (since that's the underlying storage) and then we typecast it to the element type. However, conversions from `char` to `bool` are undefined if the `char` is not `0` or `1`, so sanitizers/fuzzers will crash.

### Patches
We have patched the issue in GitHub commit [1be743703279782a357adbf9b77dcb994fe8b508](https://github.com/tensorflow/tensorflow/commit/1be743703279782a357adbf9b77dcb994fe8b508).

The fix will be included in TensorFlow 2.11.0. We will also cherrypick this commit on TensorFlow 2.10.1, TensorFlow 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability was discovered via internal fuzzing.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-pf36-r9c6-h97j
- https://nvd.nist.gov/vuln/detail/CVE-2022-41911
- https://github.com/tensorflow/tensorflow/commit/1be743703279782a357adbf9b77dcb994fe8b508
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/807cae8a807960fd7ac2313cde73a11fc15e7942/tensorflow/core/framework/tensor.cc#L1200-L1227
