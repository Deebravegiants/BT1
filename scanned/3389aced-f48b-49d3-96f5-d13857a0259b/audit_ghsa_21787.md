# [M] `CHECK`-failures during Grappler's `SafeToRemoveIdentity` in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-5f2r-qp73-37mr
CVE: CVE-2022-23579
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-5f2r-qp73-37mr
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
The Grappler optimizer in TensorFlow can be used to cause a denial of service by altering a `SavedModel` such that [`SafeToRemoveIdentity`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/optimizers/dependency_optimizer.cc#L59-L98) would trigger `CHECK` failures.

### Patches
We have patched the issue in GitHub commit [92dba16749fae36c246bec3f9ba474d9ddeb7662](https://github.com/tensorflow/tensorflow/commit/92dba16749fae36c246bec3f9ba474d9ddeb7662).
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5f2r-qp73-37mr
- https://nvd.nist.gov/vuln/detail/CVE-2022-23579
- https://github.com/tensorflow/tensorflow/commit/92dba16749fae36c246bec3f9ba474d9ddeb7662
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-88.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-143.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/optimizers/dependency_optimizer.cc#L59-L98
