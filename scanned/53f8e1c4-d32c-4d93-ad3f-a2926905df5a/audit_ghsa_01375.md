# [C] Out of bounds write in tensorflow-lite

## Summary
Severity: Critical
Advisory: GHSA-p2cq-cprg-frvm
CVE: CVE-2020-15214
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-p2cq-cprg-frvm
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
In TensorFlow Lite models using segment sum can trigger a write out bounds / segmentation fault if the segment ids are not sorted. Code assumes that the segment ids are in increasing order, using the last element of the tensor holding them to determine the dimensionality of output tensor:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/lite/kernels/segment_sum.cc#L39-L44

This results in allocating insufficient memory for the output tensor and in a write outside the bounds of the output array:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/lite/kernels/internal/reference/reference_ops.h#L2625-L2631

This usually results in a segmentation fault, but depending on runtime conditions it can provide for a write gadget to be used in future memory corruption-based exploits.

### Patches
We have patched the issue in 204945b and will release patch releases for all affected versions.

We recommend users to upgrade to TensorFlow 2.2.1, or 2.3.1.

### Workarounds
A potential workaround would be to add a custom `Verifier` to the model loading code to ensure that the segment ids are sorted, although this only handles the case when the segment ids are stored statically in the model.

A similar validation could be done if the segment ids are generated at runtime between inference steps.

If the segment ids are generated as outputs of a tensor during inference steps, then there are no possible workaround and users are advised to upgrade to patched code.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-p2cq-cprg-frvm
- https://nvd.nist.gov/vuln/detail/CVE-2020-15214
- https://github.com/tensorflow/tensorflow/commit/00c7ed7ce81c2126ebc17dfe7073b5c0efd5ec0a
- https://github.com/tensorflow/tensorflow/commit/204945b19e44b57906c9344c0d00120eeeae178a
- https://github.com/tensorflow/tensorflow/commit/a4030d8ba3692c438997c27be2dd95f3d5f54827
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-294.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-329.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-137.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/lite/kernels/internal/reference/reference_ops.h#L2625-L2631
- https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/lite/kernels/segment_sum.cc#L39-L44
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
