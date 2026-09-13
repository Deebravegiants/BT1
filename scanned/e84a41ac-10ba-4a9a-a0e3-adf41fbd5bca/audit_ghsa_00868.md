# [M] Undefined behavior in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-q8qj-fc9q-cphr
CVE: CVE-2020-15191
CWE: CWE-20, CWE-252, CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-q8qj-fc9q-cphr
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
If a user passes an invalid argument to `dlpack.to_dlpack` the expected validations will cause variables to bind to `nullptr` while setting a `status` variable to the error condition.

However, this `status` argument is not properly checked:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/c/eager/dlpack.cc#L265-L267

Hence, code following these methods will bind references to null pointers:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/c/eager/dlpack.cc#L279-L285

This is undefined behavior and reported as an error if compiling with `-fsanitize=null`.

### Patches
We have patched the issue in 22e07fb204386768e5bcbea563641ea11f96ceb8 and will release a patch release for all affected versions.

We recommend users to upgrade to TensorFlow 2.2.1 or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been discovered during variant analysis of [GHSA-rjjg-hgv6-h69v](https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rjjg-hgv6-h69v).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-q8qj-fc9q-cphr
- https://nvd.nist.gov/vuln/detail/CVE-2020-15191
- https://github.com/tensorflow/tensorflow/commit/22e07fb204386768e5bcbea563641ea11f96ceb8
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-271.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-306.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-114.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
