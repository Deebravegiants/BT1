# [H] Denial of Service in Tensorflow

## Summary
Severity: High
Advisory: GHSA-w5gh-2wr2-pm6g
CVE: CVE-2020-15206
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-w5gh-2wr2-pm6g
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
Changing the TensorFlow's `SavedModel` protocol buffer and altering the name of required keys results in segfaults and data corruption while loading the model. This can cause a denial of service in products using `tensorflow-serving` or other inference-as-a-service installments.

We have added fixes to this in f760f88b4267d981e13f4b302c437ae800445968 and fcfef195637c6e365577829c4d67681695956e7d (both going into TensorFlow 2.2.0 and 2.3.0 but not yet backported to earlier versions). However, this was not enough, as #41097 reports a different failure mode.

### Patches
We have patched the issue in adf095206f25471e864a8e63a0f1caef53a0e3a6 and will release patch releases for all versions between 1.15 and 2.3. Patch releases for versions between 1.15 and 2.1 will also contain cherry-picks of f760f88b4267d981e13f4b302c437ae800445968 and fcfef195637c6e365577829c4d67681695956e7d.

We recommend users to upgrade to TensorFlow 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Shuaike Dong, from Alipay Tian Qian Security Lab && Lab for Applied Security Research, CUHK.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-w5gh-2wr2-pm6g
- https://nvd.nist.gov/vuln/detail/CVE-2020-15206
- https://github.com/tensorflow/tensorflow/commit/adf095206f25471e864a8e63a0f1caef53a0e3a6
- https://github.com/tensorflow/tensorflow/commit/f760f88b4267d981e13f4b302c437ae800445968
- https://github.com/tensorflow/tensorflow/commit/fcfef195637c6e365577829c4d67681695956e7d
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-286.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-321.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-129.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
