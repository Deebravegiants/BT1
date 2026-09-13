# [H] Reachable Assertion in Tensorflow

## Summary
Severity: High
Advisory: GHSA-8rcj-c8pj-v3m3
CVE: CVE-2022-23564
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-8rcj-c8pj-v3m3
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
When decoding a resource handle tensor from protobuf, a TensorFlow process can encounter cases where a `CHECK` assertion is invalidated based on user controlled arguments. This allows attackers to cause denial of services in TensorFlow processes.

### Patches
We have patched the issue in GitHub commit [14fea662350e7c26eb5fe1be2ac31704e5682ee6](https://github.com/tensorflow/tensorflow/commit/14fea662350e7c26eb5fe1be2ac31704e5682ee6).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-8rcj-c8pj-v3m3
- https://nvd.nist.gov/vuln/detail/CVE-2022-23564
- https://github.com/tensorflow/tensorflow/commit/14fea662350e7c26eb5fe1be2ac31704e5682ee6
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-73.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-128.yaml
- https://github.com/tensorflow/tensorflow
