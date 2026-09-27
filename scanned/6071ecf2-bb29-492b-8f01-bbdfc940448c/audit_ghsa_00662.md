# [M] Uninitialized memory access in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-qhxx-j73r-qpm2
CVE: CVE-2020-26266
CWE: CWE-908
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2020-12-10
Source: https://github.com/advisories/GHSA-qhxx-j73r-qpm2
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
Under certain cases, a saved model can trigger use of uninitialized values during code execution. This is caused by having tensor buffers be filled with the default value of the type but forgetting to [default initialize the quantized floating point types in Eigen](https://github.com/tensorflow/tensorflow/blob/f70160322a579144950dff1537dcbe3c7c09d6f5/third_party/eigen3/unsupported/Eigen/CXX11/src/FixedPoint/FixedPointTypes.h#L61-L104):

```cc
struct QUInt8 {
  QUInt8() {}
  // ...
  uint8_t value;
};

struct QInt16 {
  QInt16() {}
  // ...
  int16_t value;
};

struct QUInt16 {
  QUInt16() {}
  // ...
  uint16_t value;
};

struct QInt32 {
  QInt32() {}
  // ...
  int32_t value;
};
```

### Patches
We have patched the issue in GitHub commit [ace0c15a22f7f054abcc1f53eabbcb0a1239a9e2](https://github.com/tensorflow/tensorflow/commit/ace0c15a22f7f054abcc1f53eabbcb0a1239a9e2) and will release TensorFlow 2.4.0 containing the patch. TensorFlow nightly packages after this commit will also have the issue resolved.

Since this issue also impacts TF versions before 2.4, we will patch all releases between 1.15 and 2.3 inclusive.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qhxx-j73r-qpm2
- https://nvd.nist.gov/vuln/detail/CVE-2020-26266
- https://github.com/tensorflow/tensorflow/commit/ace0c15a22f7f054abcc1f53eabbcb0a1239a9e2
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-297.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-332.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-254.yaml
- https://github.com/tensorflow/tensorflow
