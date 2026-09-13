# [H] Division by zero in TFLite

## Summary
Severity: High
Advisory: GHSA-gf2j-f278-xh4v
CVE: CVE-2022-23557
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-gf2j-f278-xh4v
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
An attacker can craft a TFLite model that would trigger a division by zero in [`BiasAndClamp` implementation](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/lite/kernels/internal/common.h#L75):

```cc
inline void BiasAndClamp(float clamp_min, float clamp_max, int bias_size,
                         const float* bias_data, int array_size,
                         float* array_data) {
  // ...
  TFLITE_DCHECK_EQ((array_size % bias_size), 0);
  // ...
} 
```
  
There is no check that the `bias_size` is non zero.
  
### Patches
We have patched the issue in GitHub commit [8c6f391a2282684a25cbfec7687bd5d35261a209](https://github.com/tensorflow/tensorflow/commit/8c6f391a2282684a25cbfec7687bd5d35261a209).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Wang Xuan of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gf2j-f278-xh4v
- https://nvd.nist.gov/vuln/detail/CVE-2022-23557
- https://github.com/tensorflow/tensorflow/commit/8c6f391a2282684a25cbfec7687bd5d35261a209
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-66.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-121.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/lite/kernels/internal/common.h#L75
