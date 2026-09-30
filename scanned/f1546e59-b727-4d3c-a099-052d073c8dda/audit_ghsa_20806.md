# [H] TensorFlow vulnerable to OOB read in `Gather_nd` in TF Lite

## Summary
Severity: High
Advisory: GHSA-pxrw-j2fv-hx3h
CVE: CVE-2022-35937
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-pxrw-j2fv-hx3h
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
The [`GatherNd`](https://github.com/tensorflow/tensorflow/blob/f463040eb3997e42e60a2ffc6dc72de7ef11dbb4/tensorflow/lite/kernels/gather_nd.cc#L105-L111) function takes arguments that determine the sizes of inputs and outputs. If the inputs given are greater than or equal to the sizes of the outputs, an out-of-bounds memory read is triggered.

### Patches
We have patched the issue in GitHub commit [595a65a3e224a0362d7e68c2213acfc2b499a196](https://github.com/tensorflow/tensorflow/commit/595a65a3e224a0362d7e68c2213acfc2b499a196).


The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Hui Peng from Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-pxrw-j2fv-hx3h
- https://nvd.nist.gov/vuln/detail/CVE-2022-35937
- https://github.com/tensorflow/tensorflow/commit/595a65a3e224a0362d7e68c2213acfc2b499a196
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f463040eb3997e42e60a2ffc6dc72de7ef11dbb4/tensorflow/lite/kernels/gather_nd.cc#L105-L111
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
