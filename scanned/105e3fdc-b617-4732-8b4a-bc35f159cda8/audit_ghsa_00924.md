# [H] Null pointer dereference in tensorflow-lite

## Summary
Severity: High
Advisory: GHSA-qh32-6jjc-qprm
CVE: CVE-2020-15209
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-qh32-6jjc-qprm
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
A crafted TFLite model can force a node to have as input a tensor backed by a `nullptr` buffer. This can be achieved by changing a buffer index in the flatbuffer serialization to convert a read-only tensor to a read-write one. The runtime assumes that these buffers are written to before a possible read, hence they are initialized with `nullptr`:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/lite/core/subgraph.cc#L1224-L1227

However, by changing the buffer index for a tensor and implicitly converting that tensor to be a read-write one, as there is nothing in the model that writes to it, we get a null pointer dereference.

### Patches
We have patched the issue in 0b5662bc and will release patch releases for all versions between 1.15 and 2.3.

We recommend users to upgrade to TensorFlow 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360 but was also discovered through variant analysis of [GHSA-cvpc-8phh-8f45](https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cvpc-8phh-8f45).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qh32-6jjc-qprm
- https://nvd.nist.gov/vuln/detail/CVE-2020-15209
- https://github.com/tensorflow/tensorflow/commit/0b5662bc2be13a8c8f044d925d87fb6e56247cd8
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-289.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-324.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-132.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
