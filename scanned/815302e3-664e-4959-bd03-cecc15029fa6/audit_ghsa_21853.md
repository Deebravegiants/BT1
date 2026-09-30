# [H] Division by zero in TFLite

## Summary
Severity: High
Advisory: GHSA-428x-9xc2-m8mj
CVE: CVE-2022-21741
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-428x-9xc2-m8mj
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
An attacker can craft a TFLite model that would trigger a division by zero in [the implementation of depthwise convolutions](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/lite/kernels/depthwise_conv.cc#L96).

The parameters of the convolution can be user controlled and are also used within a division operation to determine the size of the padding that needs to be added before applying the convolution. There is no check before this division that the divisor is stricly positive.

### Patches              
We have patched the issue in GitHub commit [e5b0eec199c2d03de54fd6a7fd9275692218e2bc](https://github.com/tensorflow/tensorflow/commit/e5b0eec199c2d03de54fd6a7fd9275692218e2bc).
  
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
  
### Attribution
This vulnerability has been reported by Wang Xuan of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-428x-9xc2-m8mj
- https://nvd.nist.gov/vuln/detail/CVE-2022-21741
- https://github.com/tensorflow/tensorflow/commit/e5b0eec199c2d03de54fd6a7fd9275692218e2bc
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-65.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-120.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/lite/kernels/depthwise_conv.cc#L96
