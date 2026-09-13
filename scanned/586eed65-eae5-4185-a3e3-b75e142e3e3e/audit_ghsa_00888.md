# [M] Segfault and data corruption in tensorflow-lite

## Summary
Severity: Medium
Advisory: GHSA-q4qf-3fc6-8x34
CVE: CVE-2020-15207
CWE: CWE-119, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-q4qf-3fc6-8x34
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
To mimic Python's indexing with negative values, TFLite uses `ResolveAxis` to convert negative values to positive indices. However, the only check that the converted index is now valid is only present in debug builds:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/lite/kernels/internal/reference/reduce.h#L68-L72

If the `DCHECK` does not trigger, then code execution moves ahead with a negative index. This, in turn, results in accessing data out of bounds which results in segfaults and/or data corruption.
### Patches
We have patched the issue in 2d88f470dea2671b430884260f3626b1fe99830a and will release patch releases for all versions between 1.15 and 2.3.

We recommend users to upgrade to TensorFlow 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-q4qf-3fc6-8x34
- https://nvd.nist.gov/vuln/detail/CVE-2020-15207
- https://github.com/tensorflow/tensorflow/commit/2d88f470dea2671b430884260f3626b1fe99830a
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-287.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-322.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-130.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
