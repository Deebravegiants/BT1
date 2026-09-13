# [M] CHECK-fail in LSTM with zero-length input in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-m648-33qf-v3gp
CVE: CVE-2020-26270
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2020-12-10
Source: https://github.com/advisories/GHSA-m648-33qf-v3gp
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <1.15.5
- PyPI: `tensorflow` — affected >=2.0.0 <2.0.4
- PyPI: `tensorflow` — affected >=2.1.0 <2.1.3
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.2
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.2
- PyPI: `tensorflow-cpu` — affected >=0 <1.15.5
- PyPI: `tensorflow-cpu` — affected >=2.0.0 <2.0.4
- PyPI: `tensorflow-cpu` — affected >=2.1.0 <2.1.3
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.2
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.2
- PyPI: `tensorflow-gpu` — affected >=0 <1.15.5
- PyPI: `tensorflow-gpu` — affected >=2.0.0 <2.0.4
- PyPI: `tensorflow-gpu` — affected >=2.1.0 <2.1.3
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.2
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.2

## Details
### Impact
Running an LSTM/GRU model where the LSTM/GRU layer receives an input with zero-length results in a `CHECK` failure when using the CUDA backend.

This can result in a query-of-death vulnerability, via denial of service, if users can control the input to the layer.

### Patches
We have patched the issue in GitHub commit [14755416e364f17fb1870882fa778c7fec7f16e3](https://github.com/tensorflow/tensorflow/commit/14755416e364f17fb1870882fa778c7fec7f16e3) and will release TensorFlow 2.4.0 containing the patch. TensorFlow nightly packages after this commit will also have the issue resolved.

Since this issue also impacts TF versions before 2.4, we will patch all releases between 1.15 and 2.3 inclusive.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-m648-33qf-v3gp
- https://nvd.nist.gov/vuln/detail/CVE-2020-26270
- https://github.com/tensorflow/tensorflow/commit/14755416e364f17fb1870882fa778c7fec7f16e3
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-301.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-336.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-256.yaml
- https://github.com/tensorflow/tensorflow
