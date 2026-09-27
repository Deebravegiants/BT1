# [H] Segmentation fault in tensorflow-lite

## Summary
Severity: High
Advisory: GHSA-x9j7-x98r-r4w2
CVE: CVE-2020-15210
CWE: CWE-20, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-x9j7-x98r-r4w2
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
- PyPI: `tensorflow-gpu` — affected >=0 <1.15.4
- PyPI: `tensorflow-gpu` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow-gpu` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
If a TFLite saved model uses the same tensor as both input and output of an operator, then, depending on the operator, we can observe a segmentation fault or just memory corruption.

### Patches
We have patched the issue in d58c96946b and will release patch releases for all versions between 1.15 and 2.3.

We recommend users to upgrade to TensorFlow 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

### Workarounds
A potential workaround would be to add a custom `Verifier` to the model loading code to ensure that no operator reuses tensors as both inputs and outputs. Care should be taken to check all types of inputs (i.e., constant or variable tensors as well as optional tensors).

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been discovered from a variant analysis of [GHSA-cvpc-8phh-8f45](https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cvpc-8phh-8f45).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-x9j7-x98r-r4w2
- https://nvd.nist.gov/vuln/detail/CVE-2020-15210
- https://github.com/tensorflow/tensorflow/commit/094329d0dcb8290bed2b1ee420934971f422c86d
- https://github.com/tensorflow/tensorflow/commit/1c8709b437fec10875b0cf271889afec9bbf582e
- https://github.com/tensorflow/tensorflow/commit/8c2092e9f9ef78b3f9060f8bf5ce7a49d1ccdc8f
- https://github.com/tensorflow/tensorflow/commit/d58c96946b2880991d63d1dacacb32f0a4dfa453
- https://github.com/tensorflow/tensorflow/commit/f4159ccef23d11eb58ee4263beaaeac1be3343c7
- https://github.com/tensorflow/tensorflow/commit/f50a14b00560a383865c2273e4a9094add3888d5
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-290.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-325.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-133.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
