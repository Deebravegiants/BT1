# [M] Null pointer dereference in TFLite's `Reshape` operator

## Summary
Severity: Medium
Advisory: GHSA-jjr8-m8g8-p6wv
CVE: CVE-2021-29592
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-jjr8-m8g8-p6wv
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.1.4
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.1.4
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.1.4
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.2

## Details
### Impact
The fix for [CVE-2020-15209](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-15209) missed the case when the target shape of `Reshape` operator is given by the elements of a 1-D tensor. As such, the [fix for the vulnerability](https://github.com/tensorflow/tensorflow/blob/9c1dc920d8ffb4893d6c9d27d1f039607b326743/tensorflow/lite/core/subgraph.cc#L1062-L1074) allowed passing a null-buffer-backed tensor with a 1D shape:

```cc
if (tensor->data.raw == nullptr && tensor->bytes > 0) {
  if (registration.builtin_code == kTfLiteBuiltinReshape && i == 1) {
    // In general, having a tensor here with no buffer will be an error.
    // However, for the reshape operator, the second input tensor is only
    // used for the shape, not for the data. Thus, null buffer is ok.
    continue;
  } else {
    // In all other cases, we need to return an error as otherwise we will
    // trigger a null pointer dereference (likely).
    ReportError("Input tensor %d lacks data", tensor_index);
    return kTfLiteError;
  }
}
```

### Patches
We have patched the issue in GitHub commit [f8378920345f4f4604202d4ab15ef64b2aceaa16](https://github.com/tensorflow/tensorflow/commit/f8378920345f4f4604202d4ab15ef64b2aceaa16).

The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-jjr8-m8g8-p6wv
- https://nvd.nist.gov/vuln/detail/CVE-2021-29592
- https://github.com/tensorflow/tensorflow/commit/f8378920345f4f4604202d4ab15ef64b2aceaa16
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-520.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-718.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-229.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/9c1dc920d8ffb4893d6c9d27d1f039607b326743/tensorflow/lite/core/subgraph.cc#L1062-L1074
