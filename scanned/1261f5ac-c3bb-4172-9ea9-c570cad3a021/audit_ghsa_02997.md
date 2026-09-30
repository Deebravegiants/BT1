# [M] FPE in convolutions with zero size filters

## Summary
Severity: Medium
Advisory: GHSA-6hpv-v2rx-c5g6
CVE: CVE-2021-41209
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-6hpv-v2rx-c5g6
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
The [implementations for convolution operators](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/conv_ops.cc) trigger a division by 0 if passed empty filter tensor arguments.

### Patches
We have patched the issue in GitHub commit [f2c3931113eaafe9ef558faaddd48e00a6606235](https://github.com/tensorflow/tensorflow/commit/f2c3931113eaafe9ef558faaddd48e00a6606235).
  
The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-6hpv-v2rx-c5g6
- https://nvd.nist.gov/vuln/detail/CVE-2021-41209
- https://github.com/tensorflow/tensorflow/commit/f2c3931113eaafe9ef558faaddd48e00a6606235
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-618.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-816.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-401.yaml
- https://github.com/tensorflow/tensorflow
