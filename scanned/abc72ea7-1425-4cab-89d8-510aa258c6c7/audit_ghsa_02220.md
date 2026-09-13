# [H] NPE in TFLite

## Summary
Severity: High
Advisory: GHSA-7xwj-5r4v-429p
CVE: CVE-2021-37681
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-7xwj-5r4v-429p
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
The implementation of SVDF in TFLite is [vulnerable to a null pointer error](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/lite/kernels/svdf.cc#L300-L313):

```cc
  TfLiteTensor* state = GetVariableInput(context, node, kStateTensor);
  // ...
  GetTensorData<float>(state)
```

The [`GetVariableInput` function](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/lite/kernels/kernel_util.cc#L115-L119) can return a null pointer but `GetTensorData` assumes that the argument is always a valid tensor.

```cc
TfLiteTensor* GetVariableInput(TfLiteContext* context, const TfLiteNode* node,
                               int index) {
  TfLiteTensor* tensor = GetMutableInput(context, node, index);
  return tensor->is_variable ? tensor : nullptr;
}
```

Furthermore, because `GetVariableInput` calls [`GetMutableInput`](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/lite/kernels/kernel_util.cc#L82-L90) which might return `nullptr`, the `tensor->is_variable` expression can also trigger a null pointer exception.

### Patches
We have patched the issue in GitHub commit [5b048e87e4e55990dae6b547add4dae59f4e1c76](https://github.com/tensorflow/tensorflow/commit/5b048e87e4e55990dae6b547add4dae59f4e1c76).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-7xwj-5r4v-429p
- https://nvd.nist.gov/vuln/detail/CVE-2021-37681
- https://github.com/tensorflow/tensorflow/commit/5b048e87e4e55990dae6b547add4dae59f4e1c76
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-594.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-792.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-303.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/lite/kernels/svdf.cc#L300-L313
