# [H] Integer overflow in Tensorflow

## Summary
Severity: High
Advisory: GHSA-qx3f-p745-w4hr
CVE: CVE-2022-23562
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-qx3f-p745-w4hr
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact
The implementation of `Range` suffers from integer overflows. These can trigger undefined behavior or, in some scenarios, extremely large allocations.

### Patches
We have patched the issue in GitHub commit [f0147751fd5d2ff23251149ebad9af9f03010732](https://github.com/tensorflow/tensorflow/commit/f0147751fd5d2ff23251149ebad9af9f03010732) (merging [#51733](https://github.com/tensorflow/tensorflow/pull/51733)).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/52676).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qx3f-p745-w4hr
- https://nvd.nist.gov/vuln/detail/CVE-2022-23562
- https://github.com/tensorflow/tensorflow/issues/52676
- https://github.com/tensorflow/tensorflow/pull/51733
- https://github.com/tensorflow/tensorflow/commit/f0147751fd5d2ff23251149ebad9af9f03010732
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-71.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-126.yaml
- https://github.com/tensorflow/tensorflow
