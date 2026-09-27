# [M] Heap buffer overflow due to incorrect hash function in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-hc2f-7r5r-r2hg
CVE: CVE-2022-29210
CWE: CWE-120, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hc2f-7r5r-r2hg
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1

## Details
### Impact
The [`TensorKey` hash function](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/framework/tensor_key.h#L53-L64) used total estimated `AllocatedBytes()`, which (a) is an estimate per tensor, and (b) is a very poor hash function for constants (e.g. `int32_t`).  It also tried to access individual tensor bytes through `tensor.data()` of size `AllocatedBytes()`.  This led to ASAN failures because the `AllocatedBytes()` is an estimate of total bytes allocated by a tensor, including any pointed-to constructs (e.g. strings), and does not refer to contiguous bytes in the `.data()` buffer.  We couldn't use this byte vector anyways, since types like `tstring` include pointers, whereas we need to hash the string values themselves.

### Patches
We have patched the issue in GitHub commit [1b85a28d395dc91f4d22b5f9e1e9a22e92ccecd6](https://github.com/tensorflow/tensorflow/commit/1b85a28d395dc91f4d22b5f9e1e9a22e92ccecd6).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, which is the only other affected version.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hc2f-7r5r-r2hg
- https://nvd.nist.gov/vuln/detail/CVE-2022-29210
- https://github.com/tensorflow/tensorflow/commit/1b85a28d395dc91f4d22b5f9e1e9a22e92ccecd6
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/framework/tensor_key.h#L53-L64
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
