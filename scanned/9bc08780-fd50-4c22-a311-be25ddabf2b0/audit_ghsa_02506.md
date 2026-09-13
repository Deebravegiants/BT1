# [M] Division by zero in TFLite

## Summary
Severity: Medium
Advisory: GHSA-cfpj-3q4c-jhvr
CVE: CVE-2021-37680
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-cfpj-3q4c-jhvr
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.3.4
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
The implementation of fully connected layers in TFLite is [vulnerable to a division by zero error](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/lite/kernels/fully_connected.cc#L226):

```cc
const int batch_size = input_size / filter->dims->data[1];
```

An attacker can craft a model such that `filter->dims->data[1]` is 0.

### Patches
We have patched the issue in GitHub commit [718721986aa137691ee23f03638867151f74935f](https://github.com/tensorflow/tensorflow/commit/718721986aa137691ee23f03638867151f74935f).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360. Concurrently, it has also been reported by Yakun Zhang of Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cfpj-3q4c-jhvr
- https://nvd.nist.gov/vuln/detail/CVE-2021-37680
- https://github.com/tensorflow/tensorflow/commit/718721986aa137691ee23f03638867151f74935f
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-593.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-791.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-302.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/lite/kernels/fully_connected.cc#L226
