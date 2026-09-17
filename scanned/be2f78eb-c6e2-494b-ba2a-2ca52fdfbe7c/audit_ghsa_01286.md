# [M] Segfault in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-4g9f-63rx-5cw4
CVE: CVE-2020-15190
CWE: CWE-20, CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-4g9f-63rx-5cw4
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <1.15.4
- PyPI: `tensorflow` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=0 <1.15.4
- PyPI: `tensorflow-cpu` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow-cpu` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=0 <1.15.4
- PyPI: `tensorflow-gpu` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow-gpu` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
The [`tf.raw_ops.Switch`](https://www.tensorflow.org/api_docs/python/tf/raw_ops/Switch) operation takes as input a tensor and a boolean and outputs two tensors. Depending on the boolean value, one of the tensors is exactly the input tensor whereas the other one should be an empty tensor.

However, the eager runtime traverses all tensors in the output:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/common_runtime/eager/kernel_and_device.cc#L308-L313

Since only one of the tensors is defined, the other one is `nullptr`, hence we are binding a reference to `nullptr`. This is undefined behavior and reported as an error if compiling with `-fsanitize=null`. In this case, this results in a segmentation fault

### Patches
We have patched the issue in da8558533d925694483d2c136a9220d6d49d843c and will release a patch release for all affected versions.

We recommend users to upgrade to TensorFlow 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4g9f-63rx-5cw4
- https://nvd.nist.gov/vuln/detail/CVE-2020-15190
- https://github.com/tensorflow/tensorflow/commit/da8558533d925694483d2c136a9220d6d49d843c
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-270.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-305.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-113.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
