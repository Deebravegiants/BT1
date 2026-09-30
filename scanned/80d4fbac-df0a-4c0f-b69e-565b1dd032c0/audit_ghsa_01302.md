# [M] Memory leak in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-8fxw-76px-3rxv
CVE: CVE-2020-15192
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-8fxw-76px-3rxv
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
If a user passes a list of strings to `dlpack.to_dlpack` there is a memory leak following an expected validation failure:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/c/eager/dlpack.cc#L100-L104

The allocated memory is from
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/c/eager/dlpack.cc#L256

The issue occurs because the `status` argument during validation failures is not properly checked:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/c/eager/dlpack.cc#L265-L267

Since each of the above methods can return an error status, the `status` value must be checked before continuing.

### Patches
We have patched the issue in 22e07fb204386768e5bcbea563641ea11f96ceb8 and will release a patch release for all affected versions.

We recommend users to upgrade to TensorFlow 2.2.1 or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been discovered during variant analysis of [GHSA-rjjg-hgv6-h69v](https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rjjg-hgv6-h69v).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-8fxw-76px-3rxv
- https://nvd.nist.gov/vuln/detail/CVE-2020-15192
- https://github.com/tensorflow/tensorflow/commit/22e07fb204386768e5bcbea563641ea11f96ceb8
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-272.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-307.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-115.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
