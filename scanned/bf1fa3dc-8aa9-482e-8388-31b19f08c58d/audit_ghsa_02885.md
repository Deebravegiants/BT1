# [M] Crashes due to overflow and `CHECK`-fail in ops with large tensor shapes

## Summary
Severity: Medium
Advisory: GHSA-prcg-wp5q-rv7p
CVE: CVE-2021-41197
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-prcg-wp5q-rv7p
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
TensorFlow allows tensor to have a large number of dimensions and each dimension can be as large as desired. However, the total number of elements in a tensor must fit within an `int64_t`. If an overflow occurs, `MultiplyWithoutOverflow` would return a negative result. In the majority of TensorFlow codebase this then results in a `CHECK`-failure. Newer constructs exist which return a `Status` instead of crashing the binary.

For example [`AddDim`](https://github.com/tensorflow/tensorflow/blob/0b6b491d21d6a4eb5fbab1cca565bc1e94ca9543/tensorflow/core/framework/tensor_shape.cc#L395-L408) calls should be replaced by [`AddDimWithStatus`](https://github.com/tensorflow/tensorflow/blob/0b6b491d21d6a4eb5fbab1cca565bc1e94ca9543/tensorflow/core/framework/tensor_shape.cc#L410-L440).

This is similar to [CVE-2021-29584](https://github.com/tensorflow/tensorflow/blob/3a74f0307236fe206b046689c4d76f57c9b74eee/tensorflow/security/advisory/tfsa-2021-071.md) (and similar other reported vulnerabilities in TensorFlow, localized to specific APIs).

### Patches
We have patched the issue in GitHub commits [7c1692bd417eb4f9b33ead749a41166d6080af85](https://github.com/tensorflow/tensorflow/commit/7c1692bd417eb4f9b33ead749a41166d6080af85) (merging [#51732](https://github.com/tensorflow/tensorflow/pull/51732)), [d81b1351da3e8c884ff836b64458d94e4a157c15](https://github.com/tensorflow/tensorflow/commit/d81b1351da3e8c884ff836b64458d94e4a157c15) (merging [#51717](https://github.com/tensorflow/tensorflow/pull/51717)), [a871989d7b6c18cdebf2fb4f0e5c5b62fbc19edf](https://github.com/tensorflow/tensorflow/commit/a871989d7b6c18cdebf2fb4f0e5c5b62fbc19edf) (merging [#51658](https://github.com/tensorflow/tensorflow/pull/51658)), and [d81b1351da3e8c884ff836b64458d94e4a157c15](https://github.com/tensorflow/tensorflow/commit/d81b1351da3e8c884ff836b64458d94e4a157c15) (merging [#51973](https://github.com/tensorflow/tensorflow/pull/51973)). It is possible that other similar instances exist in TensorFlow, we will issue fixes as these are discovered.

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via [GitHub issue](https://github.com/tensorflow/tensorflow/issues/46890), [GitHub issue](https://github.com/tensorflow/tensorflow/issues/51618) and [GitHub issue](https://github.com/tensorflow/tensorflow/issues/51908).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-prcg-wp5q-rv7p
- https://nvd.nist.gov/vuln/detail/CVE-2021-41197
- https://github.com/tensorflow/tensorflow/issues/46890
- https://github.com/tensorflow/tensorflow/issues/51908
- https://github.com/tensorflow/tensorflow/commit/7c1692bd417eb4f9b33ead749a41166d6080af85
- https://github.com/tensorflow/tensorflow/commit/a871989d7b6c18cdebf2fb4f0e5c5b62fbc19edf
- https://github.com/tensorflow/tensorflow/commit/d81b1351da3e8c884ff836b64458d94e4a157c15
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-607.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-805.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-390.yaml
- https://github.com/tensorflow/tensorflow
